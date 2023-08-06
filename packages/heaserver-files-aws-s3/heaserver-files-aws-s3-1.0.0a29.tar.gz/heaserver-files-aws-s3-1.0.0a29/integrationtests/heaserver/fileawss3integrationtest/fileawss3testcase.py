"""
Runs integration tests for the HEA folder service.

Note that each test opens an aiohttp server listening on port 8080.
"""

from heaserver.service.testcase import microservicetestcase, expectedvalues
from heaserver.service.testcase.mockaws import MockS3Manager
from heaserver.service.testcase.collection import CollectionKey
from heaserver.fileawss3 import service
from heaobject import user
from heaobject.data import AWSS3FileObject
import importlib.resources as pkg_resources
from heaserver.service.testcase.dockermongo import RealRegistryContainerConfig
from heaserver.service.testcase.dockermongo import DockerMongoManager
from heaserver.service.testcase.testenv import MicroserviceContainerConfig
from heaobject.registry import Resource
from heaobject.volume import DEFAULT_FILE_SYSTEM
from . import files

db_values = {
    CollectionKey(name='components', db_manager_cls=DockerMongoManager): [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Reximus',
        'invited': [],
        'modified': None,
        'name': 'reximus',
        'owner': user.NONE_USER,
        'shared_with': [],
        'source': None,
        'type': 'heaobject.registry.Component',
        'version': None,
        'base_url': 'http://localhost:8080',
        'resources': [{'type': 'heaobject.registry.Resource', 'resource_type_name': AWSS3FileObject.get_type_name(),
                       'base_path': '/volumes'}]
    }],
    CollectionKey(name='filesystems', db_manager_cls=DockerMongoManager): [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Amazon Web Services',
        'invited': [],
        'modified': None,
        'name': 'amazon_web_services',
        'owner': user.NONE_USER,
        'shared_with': [],
        'source': None,
        'type': 'heaobject.volume.AWSFileSystem',
        'version': None
    }],
    CollectionKey(name='volumes', db_manager_cls=DockerMongoManager): [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'My Amazon Web Services',
        'invited': [],
        'modified': None,
        'name': 'amazon_web_services',
        'owner': user.NONE_USER,
        'shared_with': [],
        'source': None,
        'type': 'heaobject.volume.Volume',
        'version': None,
        'file_system_name': 'amazon_web_services',
        'file_system_type': 'heaobject.volume.AWSFileSystem',
        'credential_id': None  # Let boto3 try to find the user's credentials.
    }],
    CollectionKey(name='buckets', db_manager_cls=MockS3Manager): [{
        "arn": None,
        "created": '2022-05-17T00:00:00+00:00',
        "derived_by": None,
        "derived_from": [],
        "description": None,
        "display_name": "arp-scale-2-cloud-bucket-with-tags11",
        "encrypted": True,
        "id": "arp-scale-2-cloud-bucket-with-tags11",
        "invites": [],
        "locked": False,
        "mime_type": "application/x.awsbucket",
        "modified": '2022-05-17T00:00:00+00:00',
        "name": "arp-scale-2-cloud-bucket-with-tags11",
        "object_count": None,
        "owner": "system|none",
        "permission_policy": None,
        "region": "us-west-2",
        "s3_uri": "s3://arp-scale-2-cloud-bucket-with-tags11/",
        "presigned_url": None,
        "shares": [],
        "size": None,
        "source": None,
        "tags": [],
        "type": "heaobject.bucket.AWSBucket",
        "version": None,
        "versioned": False
    }],
    CollectionKey(name='awss3files', db_manager_cls=MockS3Manager): [{
        'created': '2022-05-17T00:00:00+00:00',
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'TextFileUTF8.txt',
        'id': 'VGV4dEZpbGVVVEY4LnR4dA==',
        'invites': [],
        'modified': '2022-05-17T00:00:00+00:00',
        'name': 'VGV4dEZpbGVVVEY4LnR4dA==',
        'owner': user.NONE_USER,
        'shares': [],
        'source': 'AWS Simple Cloud Storage (S3)',
        'storage_class': 'STANDARD',
        'type': AWSS3FileObject.get_type_name(),
        's3_uri': 's3://arp-scale-2-cloud-bucket-with-tags11/TextFileUTF8.txt',
        'presigned_url': None,
        'version': None,
        'versions': [],
        'mime_type': 'text/plain',
        'size': 1253915,
        'human_readable_size': '1.3 MB',
        'bucket_id': 'arp-scale-2-cloud-bucket-with-tags11',
        'key': 'TextFileUTF8.txt',
        'tags': []
    },
        {
            'created': '2022-05-17T00:00:00+00:00',
            'derived_by': None,
            'derived_from': [],
            'description': None,
            'display_name': 'BinaryFile',
            'id': 'QmluYXJ5RmlsZQ==',
            'invites': [],
            'modified': '2022-05-17T00:00:00+00:00',
            'name': 'QmluYXJ5RmlsZQ==',
            'owner': user.NONE_USER,
            'shares': [],
            'source': 'AWS Simple Cloud Storage (S3)',
            'storage_class': 'STANDARD',
            'type': AWSS3FileObject.get_type_name(),
            's3_uri': 's3://arp-scale-2-cloud-bucket-with-tags11/BinaryFile',
            'presigned_url': None,
            'version': None,
            'versions': [],
            'mime_type': 'application/octet-stream',
            'size': 8673123,
            'human_readable_size': '8.7 MB',
            'bucket_id': 'arp-scale-2-cloud-bucket-with-tags11',
            'key': 'BinaryFile',
            'tags': []
        }
    ],
CollectionKey(name='awss3folders', db_manager_cls=MockS3Manager): [{
        'created': '2022-05-17T00:00:00+00:00',
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'TestFolder',
        'id': 'VGVzdEZvbGRlci8=',
        'invites': [],
        'modified': '2022-05-17T00:00:00+00:00',
        'name': 'VGVzdEZvbGRlci8=',
        'owner': user.NONE_USER,
        'shares': [],
        'source': 'AWS Simple Cloud Storage (S3)',
        'type': 'heaobject.folder.AWSS3Folder',
        'mime_type': 'application/x.folder',
        's3_uri': 's3://arp-scale-2-cloud-bucket-with-tags11/TestFolder/',
        'storage_class': 'STANDARD',
        'presigned_url': None,
        'bucket_id': 'arp-scale-2-cloud-bucket-with-tags11',
        'key': 'TestFolder/',
        'path': '/arp-scale-2-cloud-bucket-with-tags11/TestFolder/',
        'is_folder': True
    },
        {
            'created': '2022-05-17T00:00:00+00:00',
            'derived_by': None,
            'derived_from': [],
            'description': None,
            'display_name': 'TestFolder2',
            'id': 'VGVzdEZvbGRlcjIv',
            'invites': [],
            'modified': '2022-05-17T00:00:00+00:00',
            'name': 'VGVzdEZvbGRlcjIv',
            'owner': user.NONE_USER,
            'shares': [],
            'source': 'AWS Simple Cloud Storage (S3)',
            'type': 'heaobject.folder.AWSS3Folder',
            'mime_type': 'application/x.folder',
            's3_uri': 's3://arp-scale-2-cloud-bucket-with-tags11/TestFolder2/',
            'storage_class': 'STANDARD',
            'presigned_url': None,
            'bucket_id': 'arp-scale-2-cloud-bucket-with-tags11',
            'key': 'TestFolder2/',
            'path': '/arp-scale-2-cloud-bucket-with-tags11/TestFolder2/',
            'is_folder': True
        }]
}

content = {
    'awss3files': {
        'VGV4dEZpbGVVVEY4LnR4dA==': b'arp-scale-2-cloud-bucket-with-tags11|' + pkg_resources.read_text(files,
                                                                                                       'TextFileUTF8.txt').encode(
            'utf-8'),
        'QmluYXJ5RmlsZQ==': b'arp-scale-2-cloud-bucket-with-tags11|' + pkg_resources.read_binary(files,
                                                                                                 'BinaryFile')
    }
}

HEASERVER_REGISTRY_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-registry:1.0.0a32'
HEASERVER_VOLUMES_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-volumes:1.0.0a17'
HEASERVER_KEYCHAIN_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-keychain:1.0.0a12'
volume_microservice = MicroserviceContainerConfig(image=HEASERVER_VOLUMES_IMAGE, port=8080, check_path='/volumes',
                                                  resources=[Resource(resource_type_name='heaobject.volume.Volume',
                                                                      base_path='/volumes',
                                                                      file_system_name=DEFAULT_FILE_SYSTEM),
                                                             Resource(resource_type_name='heaobject.volume.FileSystem',
                                                                      base_path='/filesystems',
                                                                      file_system_name=DEFAULT_FILE_SYSTEM)],
                                                  db_manager_cls=DockerMongoManager)
keychain_microservice = MicroserviceContainerConfig(image=HEASERVER_KEYCHAIN_IMAGE, port=8080,
                                                    check_path='/credentials',
                                                    resources=[
                                                        Resource(resource_type_name='heaobject.keychain.Credentials',
                                                                 base_path='/credentials',
                                                                 file_system_name=DEFAULT_FILE_SYSTEM)],
                                                    db_manager_cls=DockerMongoManager)

AWSS3FileTestCase = \
    microservicetestcase.get_test_case_cls_default(
        href='http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/arp-scale-2-cloud-bucket-with-tags11/awss3files/',
        wstl_package=service.__package__,
        coll='awss3files',
        fixtures=db_values,
        content=content,
        db_manager_cls=MockS3Manager,
        get_all_actions=[
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-properties',
                rel=['hea-properties', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-open-choices',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/opener',
                rel=['hea-opener-choices', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-duplicate',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/duplicator',
                rel=['hea-duplicator', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-move',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/mover',
                rel=['hea-mover', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-versions',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/versions/',
                itemif='version is not None',
                rel=['hea-versions', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-archive',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/archive',
                rel=['hea-archive', 'hea-context-menu']
            ),
            expectedvalues.Action(
                name='heaserver-awss3files-file-unarchive',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/unarchive',
                rel=['hea-unarchive', 'hea-context-menu']
            ),
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-self',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}',
                rel=['self']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-trash',
                url='http://localhost:8080/volumes/666f6f2d6261722d71757578/awss3trash',
                wstl_url='http://localhost:8080/volumes/{volume_id}/awss3trash',
                rel=['hea-trash', 'hea-context-menu'])],
        get_actions=[
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-properties',
                rel=['hea-properties', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-open-choices',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/opener',
                rel=['hea-opener-choices', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-duplicate',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/duplicator',
                rel=['hea-duplicator', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-move',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/mover',
                rel=['hea-mover', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-versions',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/versions/',
                itemif='version is not None',
                rel=['hea-versions', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-archive',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/archive',
                rel=['hea-archive', 'hea-context-menu']
            ),
            expectedvalues.Action(
                name='heaserver-awss3files-file-unarchive',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/unarchive',
                rel=['hea-unarchive', 'hea-context-menu']
            ),
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-self',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}',
                rel=['self']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-volume',
                url='http://localhost:8080/volumes/{volume_id}',
                rel=['hea-volume']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-awsaccount',
                url='http://localhost:8080/volumes/{volume_id}/awsaccounts/me',
                rel=['hea-account']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-trash',
                url='http://localhost:8080/volumes/{volume_id}/awss3trash',
                rel=['hea-trash', 'hea-context-menu'])],
        duplicate_action_name='heaserver-awss3files-file-duplicate-form',
        duplicate_action_actions=[
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-target',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}',
                rel=['headata-target']
            )
        ],
        put_content_status=204,
        exclude=['body_post', 'body_put'],
        registry_docker_image=RealRegistryContainerConfig(HEASERVER_REGISTRY_IMAGE),
        other_docker_images=[volume_microservice, keychain_microservice])
