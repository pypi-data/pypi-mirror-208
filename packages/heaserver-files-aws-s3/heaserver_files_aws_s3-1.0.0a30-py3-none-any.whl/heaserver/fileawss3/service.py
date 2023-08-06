from heaobject.data import AWSS3FileObject
from heaobject.user import NONE_USER
from heaobject.aws import S3StorageClass, S3Version
from heaobject.root import DesktopObjectDict, Tag
from heaserver.service.oidcclaimhdrs import SUB
from heaserver.service.heaobjectsupport import new_heaobject_from_type
from heaserver.service.appproperty import HEA_DB, HEA_COMPONENT
from heaserver.service.runner import init_cmd_line, routes, start
from heaserver.service.db import awsservicelib
from heaserver.service.db.aws import S3Manager
from heaobject.awss3key import KeyDecodeException, decode_key, split, encode_key
from heaserver.service.wstl import builder_factory, action, add_run_time_action
from heaserver.service.messagebroker import publisher_cleanup_context_factory, publish_desktop_object
from heaserver.service import response
from heaserver.service.sources import AWS_S3
from heaserver.service.mimetypes import guess_mime_type
from heaserver.service.aiohttp import StreamResponseFileLikeWrapper, RequestFileLikeWrapper
from aiohttp import web, hdrs
from aiohttp.helpers import ETag
import mimetypes
import logging
from typing import Any
from functools import partial
import asyncio
from botocore.exceptions import ClientError as BotoClientError
from mypy_boto3_s3.client import S3Client

_logger = logging.getLogger(__name__)

# Non-standard mimetypes that we may assign to files in AWS S3 buckets.
MIME_TYPES = {'application/x.fastq': ['.fq', '.fastq'],  # https://en.wikipedia.org/wiki/FASTQ_format
              'application/x.vcf': ['.vcf'],  # https://en.wikipedia.org/wiki/Variant_Call_Format
              'application/x.fasta': ['.fasta', '.fa', '.fna', '.ffn', '.faa', '.frn'],  # https://en.wikipedia.org/wiki/FASTA_format
              'application/x.sam': ['.sam'],  # https://en.wikipedia.org/wiki/SAM_(file_format)
              'application/x.bam': ['.bam'],  # https://support.illumina.com/help/BS_App_RNASeq_Alignment_OLH_1000000006112/Content/Source/Informatics/BAM-Format.htm#:~:text=A%20BAM%20file%20(*.,file%20naming%20format%20of%20SampleName_S%23.
              'application/x.bambai': ['.bam.bai'],  # https://support.illumina.com/help/BS_App_RNASeq_Alignment_OLH_1000000006112/Content/Source/Informatics/BAM-Format.htm#:~:text=A%20BAM%20file%20(*.,file%20naming%20format%20of%20SampleName_S%23.
              'application/x.gff3': ['.gff'],  # https://en.wikipedia.org/wiki/General_feature_format and https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md
              'application/x.gvf': ['.gvf']  # https://github.com/The-Sequence-Ontology/Specifications/blob/master/gvf.md
             }


@routes.get('/ping')
async def ping(request: web.Request) -> web.Response:
    """
    For testing whether the service is up.

    :param request: the HTTP request.
    :return: Always returns status code 200.
    """
    return response.status_ok()


@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}')
async def get_file_options(request: web.Request) -> web.Response:
    """
    Gets the allowed HTTP methods for a file resource.

    :param request: the HTTP request (required).
    :return: the HTTP response.
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            text/plain:
                schema:
                    type: string
                    example: "200: OK"
      '404':
        $ref: '#/components/responses/404'
    """
    return await response.get_options(request, ['GET', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/duplicator')
@action(name='heaserver-awss3files-file-duplicate-form')
async def get_file_duplicator(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested file.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested file was not found.
    """
    logger = logging.getLogger(__name__)
    id_ = request.match_info['id']
    try:
        id = encode_key(split(decode_key(id_))[0])
        add_run_time_action(request, name='heaserver-awss3files-file-get-target', rel='headata-target', path=(
            '/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/' + id) if id else '/volumes/{volume_id}/buckets/{bucket_id}')
        return await _get_file(request)
    except KeyDecodeException as e:
        logger.exception('Error getting parent key')
        return response.status_bad_request(f'Error getting parent folder: {e}')


@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3files')
@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/')
async def post_file(request: web.Request) -> web.Response:
    """
    Creates a new file.

    :param request: the HTTP request. The body of the request is expected to be a file.
    :return: the response, with a 201 status code if a file was created or a 400 if not. If a folder was created, the
    Location header will contain the URL of the created file.
    ---
    summary: A specific file.
    tags:
        - heaserver-folders-folders
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
    requestBody:
        description: A new folder object.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: Folder example
                  value: {
                    "template": {
                      "data": [{
                        "name": "created",
                        "value": null
                      },
                      {
                        "name": "derived_by",
                        "value": null
                      },
                      {
                        "name": "derived_from",
                        "value": []
                      },
                      {
                        "name": "description",
                        "value": null
                      },
                      {
                        "name": "display_name",
                        "value": "Bob"
                      },
                      {
                        "name": "invited",
                        "value": []
                      },
                      {
                        "name": "modified",
                        "value": null
                      },
                      {
                        "name": "name",
                        "value": "bob"
                      },
                      {
                        "name": "owner",
                        "value": "system|none"
                      },
                      {
                        "name": "shares",
                        "value": []
                      },
                      {
                        "name": "source",
                        "value": null
                      },
                      {
                        "name": "version",
                        "value": null
                      },
                      {
                        "name": "type",
                        "value": "heaobject.folder.AWSS3Folder"
                      }]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: Item example
                  value: {
                    "created": null,
                    "derived_by": null,
                    "derived_from": [],
                    "description": null,
                    "display_name": "Joe",
                    "invited": [],
                    "modified": null,
                    "name": "joe",
                    "owner": "system|none",
                    "shares": [],
                    "source": null,
                    "type": "heaobject.folder.AWSS3Folder",
                    "version": null
                  }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.create_object(request, AWSS3FileObject)


@routes.put('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}')
async def put_file(request: web.Request) -> web.Response:
    """
    Updates file metadata.

    :param request: the HTTP request. The body of the request is expected to be a file.
    :return: the response, with a 201 status code if a file was created or a 400 if not. If a folder was created, the
    Location header will contain the URL of the created file.
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    requestBody:
        description: A new file object.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: File example
                  value: {
                    "template": {
                      "data": [{
                        "name": "created",
                        "value": null
                      },
                      {
                        "name": "derived_by",
                        "value": null
                      },
                      {
                        "name": "derived_from",
                        "value": []
                      },
                      {
                        "name": "description",
                        "value": null
                      },
                      {
                        "name": "display_name",
                        "value": "Bob"
                      },
                      {
                        "name": "invited",
                        "value": []
                      },
                      {
                        "name": "modified",
                        "value": null
                      },
                      {
                        "name": "name",
                        "value": "bob"
                      },
                      {
                        "name": "owner",
                        "value": "system|none"
                      },
                      {
                        "name": "shares",
                        "value": []
                      },
                      {
                        "name": "source",
                        "value": null
                      },
                      {
                        "name": "version",
                        "value": null
                      },
                      {
                        "name": "type",
                        "value": "heaobject.data.AWSS3FileObject"
                      }]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: Item example
                  value: {
                    "created": null,
                    "derived_by": null,
                    "derived_from": [],
                    "description": null,
                    "display_name": "Joe",
                    "invited": [],
                    "modified": null,
                    "name": "joe",
                    "owner": "system|none",
                    "shares": [],
                    "source": null,
                    "type": "heaobject.folder.AWSS3Folder",
                    "tags": [],
                    "version": null
                  }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    try:
        volume_id = request.match_info['volume_id']
        bucket_id = request.match_info['bucket_id']
        id_ = request.match_info.get('id')
    except KeyError as e:
        return response.status_bad_request(f'{e} is required')

    try:
        key = decode_key(id_)
    except KeyDecodeException as e:
        return response.status_bad_request(f'Invalid id {id_}')

    try:
        file = await new_heaobject_from_type(request, AWSS3FileObject)
    except TypeError:
        return response.status_bad_request(f'Expected type {AWSS3FileObject}; actual object was {await request.text()}')

    s3_client: S3Client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    try:
        loop = asyncio.get_running_loop()
        if key != file.key:
            await loop.run_in_executor(None, partial(s3_client.copy_object, Bucket=bucket_id, CopySource=f'{bucket_id}/{key}', Key=file.key))
            await loop.run_in_executor(None, partial(s3_client.delete_object, Bucket=bucket_id, Key=key))

        await loop.run_in_executor(None, partial(s3_client.delete_object_tagging, Bucket=bucket_id, Key=file.key))
        await loop.run_in_executor(None, partial(s3_client.put_object_tagging, Bucket=bucket_id, Key=file.key, Tagging={'TagSet': await _to_aws_tags(file.tags)}))
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)

    return await response.put(True)


@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/archive')
async def post_file_archive(request: web.Request) -> web.Response:
    """
    Posts the provided file to archive it.

    :param request: the HTTP request.
    :return: a Response object with a status of No Content.
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    requestBody:
        description: The new name of the file and target for archiving it.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: The new name of the file and target for archiving it.
                  value: {
                    "template": {
                      "data": [
                      {
                        "name": "storage_class",
                        "value": "DEEP_ARCHIVE"
                      }
                      ]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: The storage class to archive object to.
                  value: {
                    "storage_class": "DEEP_ARCHIVE"
                  }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.archive_object(request)


@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/mover')
async def post_file_mover(request: web.Request) -> web.Response:
    """
    Posts the provided file to move it.

    :param request: the HTTP request.
    :return: a Response object with a status of No Content.
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    requestBody:
        description: The new name of the file and target for moving it.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: The new name of the file and target for moving it.
                  value: {
                    "template": {
                      "data": [
                      {
                        "name": "target",
                        "value": "http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/my-bucket/awss3files/"
                      }]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: The new name of the file and target for moving it.
                  value: {
                    "target": "http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/my-bucket/awss3files/"
                  }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _move_object(request)


@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/unarchive')
async def unarchive_file(request: web.Request) -> web.Response:
    """

    :param request:
    :return: a Response object with status 202 Accept

    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.unarchive_object(request=request, activity_cb=publish_desktop_object)


@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/duplicator')
async def post_file_duplicator(request: web.Request) -> web.Response:
    """
    Posts the provided file for duplication.

    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    requestBody:
        description: The new name of the file and target for duplicating it.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: The new name of the file and target for duplicating it.
                  value: {
                    "template": {
                      "data": [
                      {
                        "name": "target",
                        "value": "http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/my-bucket"
                      }]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: The new name of the file and target for moving it.
                  value: {
                    "target": "http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/my-bucket"
                  }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _duplicate_object(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/mover')
@action(name='heaserver-awss3files-file-move-form')
async def get_file_mover(request: web.Request) -> web.Response:
    """
    Gets a form template for moving the requested file.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested file was not found.
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_file_move_template(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/archive')
@action(name='heaserver-awss3files-file-archive-form')
async def get_file_archive(request: web.Request) -> web.Response:
    """
    Gets a form template for archiving the requested file.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested file was not found.
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_file_move_template(request)


@routes.put('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/content')
async def put_file_content(request: web.Request) -> web.Response:
    """
    Updates the content of the requested file.
    :param request: the HTTP request. Required.
    :return: a Response object with the value No Content or Not Found.
    ---
    summary: File content
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    requestBody:
        description: File contents.
        required: true
        content:
            application/octet-stream:
                schema:
                    type: string
                    format: binary
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _put_object_content(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/content')
async def get_file_content(request: web.Request) -> web.StreamResponse:
    """
    :param request:
    :return:
    ---
    summary: File content
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '403':
        $ref: '#/components/responses/403'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_object_content(request)



@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}')
@action('heaserver-awss3files-file-get-open-choices', rel='hea-opener-choices hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/opener')
@action(name='heaserver-awss3files-file-get-properties', rel='hea-properties hea-context-menu')
@action(name='heaserver-awss3files-file-duplicate', rel='hea-duplicator hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/duplicator')
@action(name='heaserver-awss3files-file-move', rel='hea-mover hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/mover')
@action(name='heaserver-awss3files-file-unarchive', rel='hea-unarchive hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/unarchive')
@action(name='heaserver-awss3files-file-archive', rel='hea-archive hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/archive')
@action(name='heaserver-awss3files-file-get-trash', rel='hea-trash hea-context-menu',
        path='/volumes/{volume_id}/awss3trash')
@action(name='heaserver-awss3files-file-get-versions', rel='hea-versions hea-context-menu', itemif="version is not None",
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/versions/')
@action('heaserver-awss3files-file-get-self', rel='self', path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}')
@action(name='heaserver-awss3files-file-get-volume', rel='hea-volume', path='/volumes/{volume_id}')
@action(name='heaserver-awss3files-file-get-awsaccount', rel='hea-account', path='/volumes/{volume_id}/awsaccounts/me')
async def get_file(request: web.Request) -> web.Response:
    """
    Gets the file with the specified id.

    :param request: the HTTP request.
    :return: the requested file or Not Found.
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_file(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/byname/{name}')
@action('heaserver-awss3files-file-get-self', rel='self', path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}')
@action(name='heaserver-awss3files-file-get-volume', rel='hea-volume', path='/volumes/{volume_id}')
@action(name='heaserver-awss3files-file-get-awsaccount', rel='hea-account', path='/volumes/{volume_id}/awsaccounts/me')
async def get_file_by_name(request: web.Request) -> web.Response:
    """
    Gets the file with the specified name.

    :param request: the HTTP request.
    :return: the requested file or Not Found.
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/name'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_file_by_name(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files')
@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/')
@action('heaserver-awss3files-file-get-open-choices', rel='hea-opener-choices hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/opener')
@action(name='heaserver-awss3files-file-get-properties', rel='hea-properties hea-context-menu')
@action(name='heaserver-awss3files-file-duplicate', rel='hea-duplicator hea-context-menu', path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/duplicator')
@action(name='heaserver-awss3files-file-move', rel='hea-mover hea-context-menu', path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/mover')
@action(name='heaserver-awss3files-file-unarchive', rel='hea-unarchive hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/unarchive')
@action(name='heaserver-awss3files-file-archive', rel='hea-archive hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/archive')
@action(name='heaserver-awss3files-file-get-trash', rel='hea-trash hea-context-menu',
        path='/volumes/{volume_id}/awss3trash')
@action(name='heaserver-awss3files-file-get-versions', itemif="version is not None", rel='hea-versions hea-context-menu',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/versions/')
@action('heaserver-awss3files-file-get-self', rel='self', path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}')
async def get_files(request: web.Request) -> web.Response:
    """
    Gets the file with the specified id.

    :param request: the HTTP request.
    :return: the requested file or Not Found.
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_all_files(request)


@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{bucket_id}/awss3files')
@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{bucket_id}/awss3files/')
async def get_files_options(request: web.Request) -> web.Response:
    """
    Gets the allowed HTTP methods for a files resource.

    :param request: the HTTP request (required).
    :response: the HTTP response.
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            text/plain:
                schema:
                    type: string
                    example: "200: OK"
      '403':
        $ref: '#/components/responses/403'
      '404':
        $ref: '#/components/responses/404'
    """
    return await response.get_options(request, ['GET', 'DELETE', 'HEAD', 'OPTIONS', 'POST'])


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{file_id}/versions')
@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{file_id}/versions/')
@action(name='heaserver-awss3files-file-make-current-version', rel='hea-current-version-maker', itemif="not current",
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{file_id}/versions/{id}/currentmaker')
async def get_versions(request: web.Request) -> web.Response:
    """
    Gets all the versions of a file.

    :param request: the HTTP request.
    :return: the requested file or Not Found.
    ---
    summary: A file's versions.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - name: file_id
          in: path
          required: true
          description: The id of the file.
          schema:
            type: string
          examples:
            example:
              summary: A file id
              value: my-file
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    try:
        volume_id = request.match_info['volume_id']
        bucket_name = request.match_info['bucket_id']
        file_id = request.match_info['file_id']
    except KeyError as e:
        return response.status_bad_request(str(e))

    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    try:
        key: str | None = decode_key(file_id)
        if awsservicelib.is_folder(key):
            return response.status_bad_request(f'Object with id {file_id} is not a file')
    except KeyDecodeException:
        return response.status_bad_request(f'Invalid id {file_id}')

    versions: list[DesktopObjectDict] = []
    if await awsservicelib.is_versioning_enabled(s3_client, bucket_name):
        async for aws_version_dict in awsservicelib.list_object_versions(s3_client, bucket_name, key):
            if aws_version_dict['Key'] == key:
                version = S3Version()
                version.id = aws_version_dict['VersionId']
                version.display_name = f'Version {aws_version_dict["VersionId"]}'
                version.modified = aws_version_dict['LastModified']
                version.current = aws_version_dict['IsLatest']
                version.set_storage_class_from_str(aws_version_dict['StorageClass'])
                version.version_of_id = file_id
                versions.append(version.to_dict())
    return await response.get_all(request, versions)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{file_id}/versions/{id}')
@action(name='heaserver-awss3files-file-make-current-version', rel='hea-current-version-maker', itemif="not current",
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{file_id}/versions/{id}/currentmaker')
async def get_version(request: web.Request) -> web.Response:
    """
    Gets the version with the specified id.

    :param request: the HTTP request.
    :return: the requested version or Not Found.
    ---
    summary: A specific version of a file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - name: file_id
          in: path
          required: true
          description: The id of the file.
          schema:
            type: string
          examples:
            example:
              summary: A file id
              value: my-file
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    try:
        volume_id = request.match_info['volume_id']
        bucket_name = request.match_info['bucket_id']
        file_id = request.match_info['file_id']
        id_ = request.match_info['id']
    except KeyError as e:
        return response.status_bad_request(str(e))

    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    try:
        key: str | None = decode_key(file_id)
        if awsservicelib.is_folder(key):
            return response.status_bad_request(f'Object with id {file_id} is not a file')
    except KeyDecodeException:
        return response.status_bad_request(f'Invalid id {file_id}')

    if await awsservicelib.is_versioning_enabled(s3_client, bucket_name):
        async for aws_version_dict in awsservicelib.list_object_versions(s3_client, bucket_name, key):
            if key == aws_version_dict['Key'] and id_ == aws_version_dict['VersionId']:
                version = S3Version()
                version.id = id_
                version.display_name = f'Version {id_}'
                version.modified = aws_version_dict['LastModified']
                version.current = aws_version_dict['IsLatest']
                version.set_storage_class_from_str(aws_version_dict['StorageClass'])
                version.version_of_id = file_id
                return await response.get(request, version.to_dict())
    return await response.get(request, None)


@routes.delete('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{file_id}/versions/{id}')
async def delete_version(request: web.Request) -> web.Response:
    """
    Deletes the version with the specified id.

    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: Version deletion
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - name: file_id
          in: path
          required: true
          description: The id of the file.
          schema:
            type: string
          examples:
            example:
              summary: A file id
              value: my-file
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    try:
        volume_id = request.match_info['volume_id']
        bucket_name = request.match_info['bucket_id']
        file_id = request.match_info['file_id']
        id_ = request.match_info['id']
    except KeyError as e:
        return response.status_bad_request(str(e))

    s3_client: S3Client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    try:
        key: str | None = decode_key(file_id)
        if awsservicelib.is_folder(key):
            return response.status_bad_request(f'Object with id {file_id} is not a file')
    except KeyDecodeException:
        return response.status_bad_request(f'Invalid id {file_id}')

    delete_response = s3_client.delete_object(Bucket=bucket_name, Key=key, VersionId=id_)
    return await response.delete(delete_response.get('VersionId'))


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{file_id}/versions/{id}/currentmaker')
async def make_current_version(request: web.Request) -> web.Response:
    """
    Makes the specified version the current one.

    :param request: the HTTP request.
    :return: the response, with a 201 status code if the current version successfully changed, or a 400 if not. If
    successfully changed, the Location header will be set to the URL of the newly created version.
    ---
    summary: A specific version of a file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - name: file_id
          in: path
          required: true
          description: The id of the file.
          schema:
            type: string
          examples:
            example:
              summary: A file id
              value: my-file
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    try:
        volume_id = request.match_info['volume_id']
        bucket_name = request.match_info['bucket_id']
        file_id = request.match_info['file_id']
        id_ = request.match_info['id']
    except KeyError as e:
        return response.status_bad_request(str(e))

    s3_client: S3Client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    try:
        key: str | None = decode_key(file_id)
        if awsservicelib.is_folder(key):
            return response.status_bad_request(f'Object with id {file_id} is not a file')
    except KeyDecodeException:
        return response.status_bad_request(f'Invalid id {file_id}')

    copy_response = s3_client.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': key, 'VersionId': id_}, Key=key)
    new_version = copy_response.get('VersionId')
    if new_version is None:
        return response.status_internal_error('Operation failed')
    delete_response = s3_client.delete_object(Bucket=bucket_name, Key=key, VersionId=id_)
    if not delete_response['DeleteMarker']:
        return response.status_internal_error('Original version could not be deleted')
    return response.status_created(request.app[HEA_COMPONENT],
                                   f'volumes/{volume_id}/buckets/{bucket_name}/awss3files/{file_id}/versions',
                                   new_version)


@routes.options('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{file_id}/versions/{id}')
async def get_version_options(request: web.Request) -> web.Response:
    """
    Gets the allowed HTTP methods for a file's versions.

    :param request: the HTTP request (required).
    :response: the HTTP response.
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - name: file_id
          in: path
          required: true
          description: The id of the file.
          schema:
            type: string
          examples:
            example:
              summary: A file id
              value: my-bucket
        - $ref: '#/components/parameters/id'

    responses:
      '200':
        description: Expected response to a valid request.
        content:
            text/plain:
                schema:
                    type: string
                    example: "200: OK"
      '403':
        $ref: '#/components/responses/403'
      '404':
        $ref: '#/components/responses/404'
    """
    try:
        volume_id = request.match_info['volume_id']
        bucket_name = request.match_info['bucket_id']
        file_id = request.match_info['file_id']
        id_ = request.match_info['id']
    except KeyError as e:
        return response.status_bad_request(str(e))

    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    try:
        key: str | None = decode_key(file_id)
        if awsservicelib.is_folder(key):
            return response.status_bad_request(f'Object with id {file_id} is not a file')
    except KeyDecodeException:
        return response.status_bad_request(f'Invalid id {file_id}')

    if await awsservicelib.is_versioning_enabled(s3_client, bucket_name):
        async for aws_version_dict in awsservicelib.list_object_versions(s3_client, bucket_name, key):
            if key == aws_version_dict['Key'] and id_ == aws_version_dict['VersionId']:
                return await response.get_options(request, ['GET', 'DELETE', 'HEAD', 'OPTIONS'])

    return response.status_not_found()


@routes.delete('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}')
async def delete_file(request: web.Request) -> web.Response:
    """
    Deletes the file with the specified id.

    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: File deletion
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _delete_file(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/opener')
@action('heaserver-awss3files-file-open-default', rel='hea-opener hea-default',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/content')
@action('heaserver-awss3files-file-open-url', rel=f'hea-opener hea-context-aws {AWSS3FileObject.DEFAULT_MIME_TYPE}',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/presigned-url')
async def get_file_opener(request: web.Request) -> web.Response:
    """
    Opens the requested file.

    :param request: the HTTP request. Required.
    :return: the opened file, or Not Found if the requested file does not exist.
    ---
    summary: File opener choices
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '300':
        $ref: '#/components/responses/300'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_file(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/presigned-url')
async def generate_presigned_url(request: web.Request) -> web.Response:
    """
    Generates a  with the specified id.

    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: Presigned url for file
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: expiration
          in: query
          required: false
          description: Expiration time of presigned objects url in seconds
          schema:
            type: number
          examples:
            example:
              summary: Expiration time
              value: 259200
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _generate_presigned_url(request)


def main():
    for mime_type, extensions in MIME_TYPES.items():
        for extension in extensions if isinstance(extensions, list) else [extensions]:
            mimetypes.add_type(mime_type, extension)
    config = init_cmd_line(description='Repository of files in AWS S3 buckets', default_port=8080)
    start(package_name='heaserver-files-aws-s3', db=S3Manager,
          wstl_builder_factory=builder_factory(__package__),
          cleanup_ctx=[publisher_cleanup_context_factory(config)],
          config=config)


async def _duplicate_object(request: web.Request) -> web.Response:
    return await awsservicelib.copy_object(request)


async def _move_object(request: web.Request) -> web.Response:
    copy_response = await _duplicate_object(request)
    match copy_response.status:
        case 201:
            return await awsservicelib.delete_object(request, recursive=True)
        case _:
            return response.status_generic(copy_response.status, copy_response.text)

async def _delete_file(request: web.Request) -> web.Response:
    """
    Deletes the requested file. The volume id must be in the volume_id entry of the
    request's match_info dictionary. The bucket id must be in the bucket_id entry of the request's match_info
    dictionary. The file id must be in the id entry of the request's match_info dictionary.

    :param request: the aiohttp Request (required).
    :return: the HTTP response with a 204 status code if the file was successfully deleted, 403 if access was denied,
    404 if the file was not found, or 500 if an internal error occurred.
    """
    return await awsservicelib.delete_object(request)


async def _get_file(request: web.Request) -> web.Response:
    """
    Gets the requested file. The volume id must be in the volume_id entry of the request's match_info dictionary.
    The bucket id must be in the bucket_id entry of the request's match_info dictionary. The file id must be in
    the id entry of the request's match_info dictionary, or the file name must be in the name entry of the request's
    match_info dictionary.

    :param request: the HTTP request (required).
    :return: the HTTP response containing a heaobject.data.AWSS3FileObject object in the body.
    """
    if 'volume_id' not in request.match_info:
        return response.status_bad_request('volume_id is required')
    if 'bucket_id' not in request.match_info:
        return response.status_bad_request('bucket_id is required')
    if 'id' not in request.match_info and 'name' not in request.match_info:
        return response.status_bad_request('either id or name is required')
    volume_id = request.match_info['volume_id']
    bucket_name = request.match_info['bucket_id']
    file_name = request.match_info['id'] if 'id' in request.match_info else request.match_info['name']

    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    try:
        file_id: str | None = decode_key(file_name)
        if awsservicelib.is_folder(file_id):
            file_id = None
    except KeyDecodeException:
        # Let the bucket query happen so that we consistently return Forbidden if the user lacks permissions
        # for the bucket.
        file_id = None
    try:
        if file_id is None:
            # We couldn't decode the file_id, and we need to check if the user can access the bucket in order to
            # decide which HTTP status code to respond with (Forbidden vs Not Found).
            s3_client.head_bucket(Bucket=bucket_name)
            return response.status_not_found()
        loop = asyncio.get_running_loop()
        response_ = await loop.run_in_executor(None, partial(s3_client.list_objects_v2, Bucket=bucket_name, Prefix=file_id, MaxKeys=1))
        logging.debug('Result of get_file: %s', response_)
        if file_id is None or response_['KeyCount'] == 0:
            return response.status_not_found()
        contents = response_['Contents'][0]
        key = contents['Key']
        encoded_key = encode_key(key)
        display_name = key[key.rfind('/', 1) + 1:]
        file = await _new_file(s3_client, bucket_name, contents, display_name, key, encoded_key, request)
        return await response.get(request, file.to_dict())
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)


async def _get_versions(s3_client: S3Client, bucket_name: str, key: str,
                        loop: asyncio.AbstractEventLoop = None) -> list[dict[str, bool]] | None:
    if not loop:
        loop_ = asyncio.get_running_loop()
    else:
        loop_ = loop
    if await awsservicelib.is_versioning_enabled(s3_client, bucket_name, loop):
        vresponse = awsservicelib.list_object_versions(s3_client, bucket_name, key, loop_)
        return [version async for version in vresponse if version['Key'] == key]
    else:
        return None


async def _new_file(s3: S3Client, bucket_name: str, contents: dict[str, Any], display_name: str, key: str, encoded_key: str,
              request: web.Request) -> AWSS3FileObject:
    file = AWSS3FileObject()
    file.id = encoded_key
    file.name = encoded_key
    file.display_name = display_name
    file.modified = contents['LastModified']
    file.created = contents['LastModified']
    file.owner = request.headers.get(SUB, NONE_USER)
    file.mime_type = guess_mime_type(display_name)
    file.size = contents['Size']
    file.storage_class = S3StorageClass[contents['StorageClass']]
    file.source = AWS_S3
    file.bucket_id = bucket_name
    file.key = key
    version_dict = await awsservicelib.get_latest_object_version(s3, bucket_name, key)
    file.version = version_dict['VersionId'] if version_dict is not None else None
    object_tagging = await asyncio.get_running_loop().run_in_executor(None, partial(s3.get_object_tagging, Bucket=bucket_name, Key=key))
    tags = []
    for aws_tag in object_tagging.get('TagSet'):
        tag = Tag()
        tag.key = aws_tag['Key']
        tag.value = aws_tag['Value']
        tags.append(tag)
    file.tags = tags
    return file


async def _get_all_files(request: web.Request) -> web.Response:
    """
    Gets all files in a bucket. The volume id must be in the volume_id entry of the request's
    match_info dictionary. The bucket id must be in the bucket_id entry of the request's match_info dictionary.

    :param request: the HTTP request (required).
    :return: the HTTP response with a 200 status code if the bucket exists and a Collection+JSON document in the body
    containing any heaobject.data.AWSS3FileObject objects, 403 if access was denied, or 500 if an internal error occurred. The
    body's format depends on the Accept header in the request.
    """
    logger = logging.getLogger(__name__)
    if 'volume_id' not in request.match_info:
        return response.status_bad_request('volume_id is required')
    if 'bucket_id' not in request.match_info:
        return response.status_bad_request('bucket_id is required')
    volume_id = request.match_info['volume_id']
    bucket_name = request.match_info['bucket_id']
    s3 = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    loop = asyncio.get_running_loop()
    try:
        logger.debug('Getting all files from bucket %s', bucket_name)
        files: list[dict] = []
        async for obj in awsservicelib.list_objects(s3, bucket_id=bucket_name, loop=loop):
            key = obj['Key']
            if not awsservicelib.is_folder(key):
                encoded_key = encode_key(key)
                logger.debug('Found file %s in bucket %s', key, bucket_name)
                display_name = key.split('/')[-1]
                file = await _new_file(s3, bucket_name, obj, display_name, key, encoded_key, request)
                files.append(file.to_dict())
        return await response.get_all(request, files)
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)


async def _get_file_by_name(request: web.Request) -> web.Response:
    """
    Gets the requested file. The volume id must be in the volume_id entry of the request's match_info dictionary.
    The bucket id must be in the bucket_id entry of the request's match_info dictionary. The file name must be in the
    name entry of the request's match_info dictionary.

    :param request: the HTTP request (required).
    :return: the HTTP response with a 200 status code if the bucket exists and the heaobject.data.AWSS3FileObject in the body,
    403 if access was denied, 404 if no such file was found, or 500 if an internal error occurred. The body's format
    depends on the Accept header in the request.
    """
    return await _get_file(request)


async def _has_file(request: web.Request) -> web.Response:
    """
    Checks for the existence of the requested file object. The volume id must be in the volume_id entry of the
    request's match_info dictionary. The bucket id must be in the bucket_id entry of the request's match_info
    dictionary. The file id must be in the id entry of the request's match_info dictionary.

    :param request: the HTTP request (required).
    :return: the HTTP response with a 200 status code if the file exists, 403 if access was denied, or 500 if an
    internal error occurred.
    """
    logger = logging.getLogger(__name__)

    if 'volume_id' not in request.match_info:
        return response.status_bad_request('volume_id is required')
    if 'bucket_id' not in request.match_info:
        return response.status_bad_request('bucket_id is required')
    if 'id' not in request.match_info:
        return response.status_bad_request('id is required')

    volume_id = request.match_info['volume_id']
    bucket_name = request.match_info['bucket_id']

    s3 = await request.app[HEA_DB].get_client(request, 's3', volume_id)

    try:
        file_id: str | None = decode_key(request.match_info['id'])
        if awsservicelib.is_folder(file_id):
            file_id = None
    except KeyDecodeException:
        # Let the bucket query happen so that we consistently return Forbidden if the user lacks permissions
        # for the bucket.
        file_id = None
    loop = asyncio.get_running_loop()
    try:
        if file_id is None:
            # We couldn't decode the file_id, and we need to check if the user can access the bucket in order to
            # decide which HTTP status code to respond with (Forbidden vs Not Found).
            await loop.run_in_executor(None, partial(s3.head_bucket, Bucket=bucket_name))
            return response.status_not_found()
        logger.debug('Checking if file %s in bucket %s exists', file_id, bucket_name)
        response_ = await loop.run_in_executor(None, partial(s3.list_objects_v2, Bucket=bucket_name, Prefix=file_id,
                                                             MaxKeys=1))
        if response_['KeyCount'] > 0:
            return response.status_ok()
        return await response.get(request, None)
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)
    except KeyDecodeException:
        return response.status_not_found()


async def _get_object_content(request: web.Request) -> web.StreamResponse:
    """
    preview object in object explorer
    :param request: the aiohttp Request (required).
    """
    logger = logging.getLogger(__name__)
    if 'volume_id' not in request.match_info:
        return response.status_bad_request('volume_id is required')
    if 'bucket_id' not in request.match_info:
        return response.status_bad_request('bucket_id is required')
    if 'id' not in request.match_info:
        return response.status_bad_request('id is required')
    volume_id = request.match_info['volume_id']
    bucket_name = request.match_info['bucket_id']
    file_name = request.match_info['id']

    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)

    try:
        key: str | None = decode_key(file_name)
        if awsservicelib.is_folder(key):
            key = None
    except KeyDecodeException:
        # Let the bucket query happen so that we consistently return Forbidden if the user lacks permissions
        # for the bucket.
        key = None

    try:
        loop = asyncio.get_running_loop()
        if key is None:
            # We couldn't decode the file_id, and we need to check if the user can access the bucket in order to
            # decide which HTTP status code to respond with (Forbidden vs Not Found).
            await loop.run_in_executor(None, partial(s3_client.head_bucket, Bucket=bucket_name))
            return response.status_not_found()
        resp = await loop.run_in_executor(None, partial(s3_client.head_object, Bucket=bucket_name, Key=key))
        etag = resp['ETag'].strip('"')
        last_modified = resp['LastModified']
        if request.if_none_match and ETag(etag) in request.if_none_match:
            return web.HTTPNotModified()
        if request.if_modified_since and last_modified and request.if_modified_since >= last_modified:
            return web.HTTPNotModified()
        logger.debug('Downloading object %s', resp)

        response_ = web.StreamResponse(status=200, reason='OK',
                                       headers={hdrs.CONTENT_DISPOSITION: f'attachment; filename={key.split("/")[-1]}'})
        mime_type = guess_mime_type(key)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        response_.content_type = mime_type
        response_.last_modified = last_modified
        response_.content_length = resp['ContentLength']
        response_.etag = etag
        await response_.prepare(request)
        async with StreamResponseFileLikeWrapper(response_) as fileobj:
            logger.debug('After initialize')
            await loop.run_in_executor(None, s3_client.download_fileobj, bucket_name, key, fileobj)
        logger.debug('Content length is %d bytes', response_.content_length)
        return response_
    except BotoClientError:
        logger.exception('Error getting object content')
        return response.status_not_found()


async def _generate_presigned_url(request: web.Request):
    """Generate a presigned URL to share an S3 object

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param path_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as a string. If error, returns 404.

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
    """
    # Generate a presigned URL for the S3 object
    volume_id = request.match_info['volume_id']
    bucket_id = request.match_info['bucket_id']
    object_id = request.match_info['id']
    # three days default for expiration
    expiration = request.rel_url.query.get("expiration", 259200)

    try:
        object_id = decode_key(object_id)
    except KeyDecodeException:
        # Let the bucket query happen so that we consistently return Forbidden if the user lacks permissions
        # for the bucket.
        return response.status_not_found()
    try:
        s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
        loop = asyncio.get_running_loop()
        url = await loop.run_in_executor(None, partial(s3_client.generate_presigned_url, 'get_object',
                                                       Params={'Bucket': bucket_id, 'Key': object_id},
                                                       ExpiresIn=expiration))
        logging.info(response)
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)
    # The response contains the presigned URL
    file = AWSS3FileObject()
    file.presigned_url = url
    return await response.get(request, file.to_dict())


async def _put_object_content(request: web.Request) -> web.Response:
    """
    Upload a file to an S3 bucket. Will fail if the file already exists.
    See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html for more information.

    The following information must be specified in request.match_info:
    volume_id (str): the id of the target volume,
    bucket_id (str): the name of the target bucket,
    id (str): the name of the file.

    :param request: the aiohttp Request (required).
    :return: the HTTP response, with a 204 status code if successful, 400 if one of the above values was not specified,
    403 if uploading access was denied, 404 if the volume or bucket could not be found, or 500 if an internal error
    occurred.
    """
    logger = logging.getLogger(__name__)
    if 'volume_id' not in request.match_info:
        return response.status_bad_request("volume_id is required")
    if 'bucket_id' not in request.match_info:
        return response.status_bad_request("bucket_id is required")
    if 'id' not in request.match_info:
        return response.status_bad_request('id is required')
    volume_id = request.match_info['volume_id']
    bucket_name = request.match_info['bucket_id']
    file_name = request.match_info['id']

    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    loop = asyncio.get_running_loop()

    try:
        file_id: str | None = decode_key(file_name)
        if awsservicelib.is_folder(file_id):
            file_id = None
    except KeyDecodeException:
        # Let the bucket query happen so that we consistently return Forbidden if the user lacks permissions
        # for the bucket.
        file_id = None

    try:
        if file_id is None:
            # We couldn't decode the file_id, and we need to check if the user can access the bucket in order to
            # decide which HTTP status code to respond with (Forbidden vs Not Found).
            await loop.run_in_executor(None, partial(s3_client.head_bucket, Bucket=bucket_name))
            return response.status_not_found()
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)

    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    try:
        await loop.run_in_executor(None, partial(s3_client.head_object, Bucket=bucket_name, Key=file_id))
        fileobj = RequestFileLikeWrapper(request)
        done = False
        try:
            fileobj.initialize()
            upload_response = await loop.run_in_executor(None, s3_client.upload_fileobj, fileobj, bucket_name, file_id)
            logger.info(upload_response)
            fileobj.close()
            done = True
        except Exception as e:
            if not done:
                try:
                    fileobj.close()
                except:
                    pass
                done = True
                raise e
    except BotoClientError as e:
        return awsservicelib.handle_client_error(e)
    return response.status_no_content()


async def _get_file_move_template(request: web.Request) -> web.Response:
    logger = logging.getLogger(__name__)
    id_ = request.match_info['id']
    try:
        id = encode_key(split(decode_key(id_))[0])
        add_run_time_action(request, name='heaserver-awss3files-file-get-target', rel='headata-target', path=(
            '/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/' + id) if id else '/volumes/{volume_id}/buckets/{bucket_id}')
        return await _get_file(request)
    except KeyDecodeException as e:
        logger.exception('Error getting parent key')
        return response.status_bad_request(f'Error getting parent folder: {e}')


async def _to_aws_tags(hea_tags: list[Tag]) -> list[dict[str, str]]:
    """
    :param hea_tags: HEA tags to converted to aws tags compatible with boto3 api
    :return: aws tags
    """
    aws_tag_dicts = []
    for hea_tag in hea_tags:
        aws_tag_dict = {}
        aws_tag_dict['Key'] = hea_tag.key
        aws_tag_dict['Value'] = hea_tag.value
        aws_tag_dicts.append(aws_tag_dict)
    return aws_tag_dicts
