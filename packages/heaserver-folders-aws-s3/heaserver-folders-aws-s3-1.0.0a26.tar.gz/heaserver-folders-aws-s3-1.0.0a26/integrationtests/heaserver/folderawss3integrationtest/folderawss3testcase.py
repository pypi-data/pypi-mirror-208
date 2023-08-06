"""
Runs integration tests for the HEA folder service.

Note that each test opens an aiohttp server listening on port 8080.
"""

from heaserver.service.testcase import expectedvalues
from heaserver.service.testcase.awss3microservicetestcase import with_docker_images, \
    get_test_case_cls_default_with_message_broker
from heaserver.service.testcase.dockermongo import DockerMongoManager, RealRegistryContainerConfig
from heaserver.service.testcase.testenv import MicroserviceContainerConfig
from heaserver.service.testcase.collection import get_collection_key_from_name
from heaobject.registry import Resource
from heaserver.folderawss3 import service
from heaserver.service.testcase.mockaws import MockS3Manager
from heaserver.service.testcase.collection import CollectionKey
from heaobject import user
from base64 import b64encode

db_values = {
    CollectionKey(name='awss3folders_items', db_manager_cls=MockS3Manager): [
        {
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
            'type': 'heaobject.folder.AWSS3FolderFileItem',
            'actual_object_type_name': 'heaobject.folder.AWSS3Folder',
            'actual_object_id': 'VGVzdEZvbGRlci8=',
            'actual_object_uri': '/volumes/666f6f2d6261722d71757578/buckets/arp-scale-2-cloud-bucket-with-tags11/awss3folders/VGVzdEZvbGRlci8=',
            's3_uri': 's3://arp-scale-2-cloud-bucket-with-tags11/TestFolder/',
            'storage_class': 'STANDARD',
            'size': None,
            'human_readable_size': None,
            'volume_id': '666f6f2d6261722d71757578',
            'folder_id': 'root',
            'bucket_id': 'arp-scale-2-cloud-bucket-with-tags11',
            'key': 'TestFolder/',
            'path': '/arp-scale-2-cloud-bucket-with-tags11/TestFolder/',
            'is_folder': True,
            'mime_type': 'application/x.item'
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
            'type': 'heaobject.folder.AWSS3FolderFileItem',
            'actual_object_type_name': 'heaobject.folder.AWSS3Folder',
            'actual_object_id': 'VGVzdEZvbGRlcjIv',
            'actual_object_uri': '/volumes/666f6f2d6261722d71757578/buckets/arp-scale-2-cloud-bucket-with-tags11/awss3folders/VGVzdEZvbGRlcjIv',
            's3_uri': 's3://arp-scale-2-cloud-bucket-with-tags11/TestFolder2/',
            'storage_class': 'STANDARD',
            'size': None,
            'human_readable_size': None,
            'volume_id': '666f6f2d6261722d71757578',
            'folder_id': 'root',
            'bucket_id': 'arp-scale-2-cloud-bucket-with-tags11',
            'key': 'TestFolder2/',
            'path': '/arp-scale-2-cloud-bucket-with-tags11/TestFolder2/',
            'is_folder': True,
            'mime_type': 'application/x.item'
        }
    ],
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
        'base_url': 'http://localhost:8080',
        'resources': [{'type': 'heaobject.registry.Resource', 'resource_type_name': 'heaobject.folder.AWSS3Folder',
                       'base_path': '/volumes/666f6f2d6261722d71757578/buckets/arp-scale-2-cloud-bucket-with-tags11/awss3folders'},
                      {'type': 'heaobject.registry.Resource',
                       'resource_type_name': 'heaobject.folder.AWSS3FolderFileItem',
                       'base_path': '/items'}]
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
        'type': 'heaobject.volume.AWSFileSystem'
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
        'presigned_url': None,
        "shares": [],
        "size": None,
        "source": None,
        "tags": [],
        "type": "heaobject.bucket.AWSBucket",
        "versioned": False
    }],
    CollectionKey(name='awsaccounts', db_manager_cls=MockS3Manager): [{
        'email_address': 'no-reply@example.com',
        'alternate_contact_name': None,
        "alternate_email_address": None,
        "alternate_phone_number": None,
        "created": '2022-05-17T00:00:00+00:00',
        "derived_by": None,
        "derived_from": [],
        "description": None,
        "display_name": "311813441058",
        "full_name": None,
        "id": "311813441058",
        "invites": [],
        "mime_type": "application/x.awsaccount",
        "modified": '2022-05-17T00:00:00+00:00',
        "name": "311813441058",
        "owner": "system|none",
        "phone_number": None,
        "shares": [],
        "source": None,
        "type": "heaobject.account.AWSAccount"
    }],
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

content_ = [{'collection': {'version': '1.0', 'href': 'http://localhost:8080/folders/root/items/', 'items': [{'data': [
    {'name': 'created', 'value': None, 'prompt': 'created', 'display': True},
    {'name': 'derived_by', 'value': None, 'prompt': 'derived_by', 'display': True},
    {'name': 'derived_from', 'value': [], 'prompt': 'derived_from', 'display': True},
    {'name': 'description', 'value': None, 'prompt': 'description', 'display': True},
    {'name': 'display_name', 'value': 'Reximus', 'prompt': 'display_name', 'display': True},
    {'name': 'id', 'value': '666f6f2d6261722d71757578', 'prompt': 'id', 'display': False},
    {'name': 'invites', 'value': [], 'prompt': 'invites', 'display': True},
    {'name': 'modified', 'value': None, 'prompt': 'modified', 'display': True},
    {'name': 'name', 'value': 'reximus', 'prompt': 'name', 'display': True},
    {'name': 'owner', 'value': 'system|none', 'prompt': 'owner', 'display': True},
    {'name': 'shares', 'value': [], 'prompt': 'shares', 'display': True},
    {'name': 'source', 'value': None, 'prompt': 'source', 'display': True},
    {'name': 'actual_object_type_name', 'value': 'heaobject.folder.Folder', 'prompt': 'actual_object_type_name',
     'display': True},
    {'name': 'actual_object_id', 'value': '666f6f2d6261722d71757579', 'prompt': 'actual_object_id', 'display': True},
    {'name': 'folder_id', 'value': 'root', 'prompt': 'folder_id', 'display': True},
    {'name': 'bucket_id', 'value': 'arp-scale-2-cloud-bucket-with-tags11', 'prompt': 'bucket_id', 'display': True},
    {'name': 'key', 'value': 'Reximus/', 'prompt': 'key', 'display': True},
    {'section': 'actual_object', 'name': 'created', 'value': None, 'prompt': 'created', 'display': True},
    {'section': 'actual_object', 'name': 'derived_by', 'value': None, 'prompt': 'derived_by', 'display': True},
    {'section': 'actual_object', 'name': 'derived_from', 'value': [], 'prompt': 'derived_from', 'display': True},
    {'section': 'actual_object', 'name': 'description', 'value': None, 'prompt': 'description', 'display': True},
    {'section': 'actual_object', 'name': 'display_name', 'value': 'Reximus', 'prompt': 'display_name', 'display': True},
    {'section': 'actual_object', 'name': 'id', 'value': '666f6f2d6261722d71757579', 'prompt': 'id', 'display': False},
    {'section': 'actual_object', 'name': 'invites', 'value': [], 'prompt': 'invites', 'display': True},
    {'section': 'actual_object', 'name': 'modified', 'value': None, 'prompt': 'modified', 'display': True},
    {'section': 'actual_object', 'name': 'name', 'value': 'reximus', 'prompt': 'name', 'display': True},
    {'section': 'actual_object', 'name': 'owner', 'value': 'system|none', 'prompt': 'owner', 'display': True},
    {'section': 'actual_object', 'name': 'shares', 'value': [], 'prompt': 'shares', 'display': True},
    {'section': 'actual_object', 'name': 'source', 'value': None, 'prompt': 'source', 'display': True},
    {'section': 'actual_object', 'name': 'version', 'value': None, 'prompt': 'version', 'display': True}], 'links': [{'prompt': 'Move', 'rel': 'mover',
                                   'href': 'http://localhost:8080/folders/root/items/666f6f2d6261722d71757578/mover'},
                                  {'prompt': 'Open', 'rel': 'hea-opener-choices',
                                   'href': 'http://localhost:8080/folders/root/items/666f6f2d6261722d71757578/opener'},
                                  {'prompt': 'Duplicate', 'rel': 'duplicator',
                                   'href': 'http://localhost:8080/folders/root/items/666f6f2d6261722d71757578/duplicator'}]}],
                            'template': {'prompt': 'Properties', 'rel': 'properties', 'data': [
                                {'name': 'id', 'value': '666f6f2d6261722d71757578', 'prompt': 'Id', 'required': True,
                                 'readOnly': True, 'pattern': ''},
                                {'name': 'source', 'value': None, 'prompt': 'Source', 'required': False,
                                 'readOnly': False, 'pattern': ''},
                                {'name': 'version', 'value': None, 'prompt': 'Version', 'required': False,
                                 'readOnly': False, 'pattern': ''},
                                {'name': 'display_name', 'value': 'Reximus', 'prompt': 'Name', 'required': True,
                                 'readOnly': False, 'pattern': ''},
                                {'name': 'description', 'value': None, 'prompt': 'Description', 'required': False,
                                 'readOnly': False, 'pattern': ''},
                                {'name': 'owner', 'value': 'system|none', 'prompt': 'Owner', 'required': False,
                                 'readOnly': False, 'pattern': ''},
                                {'name': 'created', 'value': None, 'prompt': 'Created', 'required': False,
                                 'readOnly': True, 'pattern': ''},
                                {'name': 'modified', 'value': None, 'prompt': 'Modified', 'required': False,
                                 'readOnly': True, 'pattern': ''},
                                {'name': 'invites', 'value': [], 'prompt': 'Share invites', 'required': False,
                                 'readOnly': True, 'pattern': ''},
                                {'name': 'shares', 'value': [], 'prompt': 'Shared with', 'required': False,
                                 'readOnly': False, 'pattern': ''},
                                {'name': 'derived_by', 'value': None, 'prompt': 'Derived by', 'required': False,
                                 'readOnly': True, 'pattern': ''},
                                {'name': 'derived_from', 'value': [], 'prompt': 'Derived from', 'required': False,
                                 'readOnly': True, 'pattern': ''},
                                {'name': 'items', 'value': None, 'prompt': 'Items', 'required': False, 'readOnly': True,
                                 'pattern': ''}]}}}, {
                'collection': {'version': '1.0', 'href': 'http://localhost:8080/folders/root/items/', 'items': [{
                    'data': [
                        {
                            'name': 'created',
                            'value': None,
                            'prompt': 'created',
                            'display': True},
                        {
                            'name': 'derived_by',
                            'value': None,
                            'prompt': 'derived_by',
                            'display': True},
                        {
                            'name': 'derived_from',
                            'value': [],
                            'prompt': 'derived_from',
                            'display': True},
                        {
                            'name': 'description',
                            'value': None,
                            'prompt': 'description',
                            'display': True},
                        {
                            'name': 'display_name',
                            'value': 'Reximus',
                            'prompt': 'display_name',
                            'display': True},
                        {
                            'name': 'id',
                            'value': '0123456789ab0123456789ab',
                            'prompt': 'id',
                            'display': False},
                        {
                            'name': 'invites',
                            'value': [],
                            'prompt': 'invites',
                            'display': True},
                        {
                            'name': 'modified',
                            'value': None,
                            'prompt': 'modified',
                            'display': True},
                        {
                            'name': 'name',
                            'value': 'reximus',
                            'prompt': 'name',
                            'display': True},
                        {
                            'name': 'owner',
                            'value': 'system|none',
                            'prompt': 'owner',
                            'display': True},
                        {
                            'name': 'shares',
                            'value': [],
                            'prompt': 'shares',
                            'display': True},
                        {
                            'name': 'source',
                            'value': None,
                            'prompt': 'source',
                            'display': True},
                        {
                            'name': 'actual_object_type_name',
                            'value': 'heaobject.folder.Folder',
                            'prompt': 'actual_object_type_name',
                            'display': True},
                        {
                            'name': 'actual_object_id',
                            'value': '0123456789ab0123456789ac',
                            'prompt': 'actual_object_id',
                            'display': True},
                        {
                            'name': 'folder_id',
                            'value': 'root',
                            'prompt': 'folder_id',
                            'display': True},
                        {
                            'section': 'actual_object',
                            'name': 'created',
                            'value': None,
                            'prompt': 'created',
                            'display': True},
                        {
                            'section': 'actual_object',
                            'name': 'derived_by',
                            'value': None,
                            'prompt': 'derived_by',
                            'display': True},
                        {
                            'section': 'actual_object',
                            'name': 'derived_from',
                            'value': [],
                            'prompt': 'derived_from',
                            'display': True},
                        {
                            'section': 'actual_object',
                            'name': 'description',
                            'value': None,
                            'prompt': 'description',
                            'display': True},
                        {
                            'section': 'actual_object',
                            'name': 'display_name',
                            'value': 'Reximus',
                            'prompt': 'display_name',
                            'display': True},
                        {
                            'section': 'actual_object',
                            'name': 'id',
                            'value': '0123456789ab0123456789ac',
                            'prompt': 'id',
                            'display': False},
                        {
                            'section': 'actual_object',
                            'name': 'invites',
                            'value': [],
                            'prompt': 'invites',
                            'display': True},
                        {
                            'section': 'actual_object',
                            'name': 'modified',
                            'value': None,
                            'prompt': 'modified',
                            'display': True},
                        {
                            'section': 'actual_object',
                            'name': 'name',
                            'value': 'reximus',
                            'prompt': 'name',
                            'display': True},
                        {
                            'section': 'actual_object',
                            'name': 'owner',
                            'value': 'system|none',
                            'prompt': 'owner',
                            'display': True},
                        {
                            'section': 'actual_object',
                            'name': 'shares',
                            'value': [],
                            'prompt': 'shares',
                            'display': True},
                        {
                            'section': 'actual_object',
                            'name': 'source',
                            'value': None,
                            'prompt': 'source',
                            'display': True},
                        {
                            'section': 'actual_object',
                            'name': 'version',
                            'value': None,
                            'prompt': 'version',
                            'display': True},
                        {'name': 'bucket_id', 'value': 'arp-scale-2-cloud-bucket-with-tags11', 'prompt': 'bucket_id',
                         'display': True},
                        {'name': 'key', 'value': 'Reximus/', 'prompt': 'key', 'display': True}],
                    'links': [
                        {
                            'prompt': 'Move',
                            'rel': 'mover',
                            'href': 'http://localhost:8080/folders/root/items/0123456789ab0123456789ab/mover'},
                        {
                            'prompt': 'Open',
                            'rel': 'hea-opener-choices',
                            'href': 'http://localhost:8080/folders/root/items/0123456789ab0123456789ab/opener'},
                        {
                            'prompt': 'Duplicate',
                            'rel': 'duplicator',
                            'href': 'http://localhost:8080/folders/root/items/0123456789ab0123456789ab/duplicator'}]}],
                               'template': {'prompt': 'Properties', 'rel': 'properties', 'data': [
                                   {'name': 'id', 'value': '0123456789ab0123456789ab', 'prompt': 'Id', 'required': True,
                                    'readOnly': True, 'pattern': ''},
                                   {'name': 'source', 'value': None, 'prompt': 'Source', 'required': False,
                                    'readOnly': False, 'pattern': ''},
                                   {'name': 'version', 'value': None, 'prompt': 'Version', 'required': False,
                                    'readOnly': False, 'pattern': ''},
                                   {'name': 'display_name', 'value': 'Reximus', 'prompt': 'Name', 'required': True,
                                    'readOnly': False, 'pattern': ''},
                                   {'name': 'description', 'value': None, 'prompt': 'Description', 'required': False,
                                    'readOnly': False, 'pattern': ''},
                                   {'name': 'owner', 'value': 'system|none', 'prompt': 'Owner', 'required': False,
                                    'readOnly': False, 'pattern': ''},
                                   {'name': 'created', 'value': None, 'prompt': 'Created', 'required': False,
                                    'readOnly': True, 'pattern': ''},
                                   {'name': 'modified', 'value': None, 'prompt': 'Modified', 'required': False,
                                    'readOnly': True, 'pattern': ''},
                                   {'name': 'invites', 'value': [], 'prompt': 'Share invites', 'required': False,
                                    'readOnly': True, 'pattern': ''},
                                   {'name': 'shares', 'value': [], 'prompt': 'Shared with', 'required': False,
                                    'readOnly': False, 'pattern': ''},
                                   {'name': 'derived_by', 'value': None, 'prompt': 'Derived by', 'required': False,
                                    'readOnly': True, 'pattern': ''},
                                   {'name': 'derived_from', 'value': [], 'prompt': 'Derived from', 'required': False,
                                    'readOnly': True, 'pattern': ''},
                                   {'name': 'items', 'value': None, 'prompt': 'Items', 'required': False,
                                    'readOnly': True, 'pattern': ''}]}}}]

content = {
    'folders': {
        '666f6f2d6261722d71757579': content_
    }
}

HEASERVER_REGISTRY_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-registry:1.0.0a33'
HEASERVER_ACTIVITY_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-activity:1.0.0a8'

activity = MicroserviceContainerConfig(
    image=HEASERVER_ACTIVITY_IMAGE, port=8080,
    check_path='/activity',
    db_manager_cls=DockerMongoManager,
    resources=[Resource(resource_type_name='heaobject.activity.AWSActivity',
                        base_path='/activity')])

get_test_case_cls_default = with_docker_images(get_test_case_cls_default_with_message_broker, activity)
get_test_case_cls_default.__doc__ = """
    The same as awss3microservicetestcase.get_test_case_cls_default_with_message_broker except it also starts a
    HEA Activity Microservice container.
"""

AWSS3FolderTestCase = \
    get_test_case_cls_default(
        href='http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/arp-scale-2-cloud-bucket-with-tags11/awss3folders/',
        wstl_package=service.__package__,
        coll='awss3folders',
        fixtures=db_values,
        db_manager_cls=MockS3Manager,
        get_all_actions=[
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-get-open-choices',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/opener',
                rel=['hea-opener-choices', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-duplicate',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/duplicator',
                rel=['hea-duplicator', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-move',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/mover',
                rel=['hea-mover', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-get-properties',
                rel=['hea-properties', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-archive',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/archive',
                rel=['hea-archive', 'hea-context-menu']
            ),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-unarchive',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/unarchive',
                rel=['hea-unarchive', 'hea-context-menu']
            ),
            expectedvalues.Action(name='heaserver-awss3folders-folder-get-self',
                                  url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}',
                                  rel=['self']),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-get-create-choices',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/creator',
                rel=['hea-creator-choices', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-get-trash',
                url='http://localhost:8080/volumes/666f6f2d6261722d71757578/awss3trash',
                wstl_url='http://localhost:8080/volumes/{volume_id}/awss3trash',
                rel=['hea-trash', 'hea-context-menu'])
        ],
        get_actions=[
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-get-open-choices',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/opener',
                rel=['hea-opener-choices', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-duplicate',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/duplicator',
                rel=['hea-duplicator', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-move',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/mover',
                rel=['hea-mover', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-get-properties',
                rel=['hea-properties', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-archive',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/archive',
                rel=['hea-archive', 'hea-context-menu']
            ),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-unarchive',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/unarchive',
                rel=['hea-unarchive', 'hea-context-menu']
            ),
            expectedvalues.Action(name='heaserver-awss3folders-folder-get-self',
                                  url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}',
                                  rel=['self']),
            expectedvalues.Action(name='heaserver-awss3folders-folder-get-volume',
                                  url='http://localhost:8080/volumes/{volume_id}',
                                  rel=['hea-volume']),
            expectedvalues.Action(name='heaserver-awss3folders-folder-get-awsaccount',
                                  url='http://localhost:8080/volumes/{volume_id}/awsaccounts/me',
                                  rel=['hea-account']),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-get-create-choices',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3folders/{id}/creator',
                rel=['hea-creator-choices', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-get-trash',
                url='http://localhost:8080/volumes/{volume_id}/awss3trash',
                rel=['hea-trash', 'hea-context-menu'])
        ],
        duplicate_action_name='heaserver-awss3folders-folder-duplicate-form',
        duplicate_action_actions=[
            expectedvalues.Action(
                name='heaserver-awss3folders-folder-get-target',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}',
                rel=['headata-target']
            )
        ],
        registry_docker_image=RealRegistryContainerConfig(HEASERVER_REGISTRY_IMAGE),
        exclude=['body_put', 'body_post']
    )


class AWSS3ItemTestCase(
    get_test_case_cls_default_with_message_broker(
        href='http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/arp-scale-2-cloud-bucket-with-tags11/awss3folders/root/items/',
        wstl_package=service.__package__,
        coll='awss3folders_items',
        fixtures=db_values,
        db_manager_cls=MockS3Manager,
        get_all_actions=[
            expectedvalues.Action(
                name='heaserver-awss3folders-item-get-actual',
                url='http://localhost:8080{+actual_object_uri}',
                rel=['hea-actual'])
        ],
        get_actions=[
            expectedvalues.Action(
                name='heaserver-awss3folders-item-get-actual',
                url='http://localhost:8080{+actual_object_uri}',
                rel=['hea-actual']),
            expectedvalues.Action(name='heaserver-awss3folders-item-get-volume',
                                  url='http://localhost:8080/volumes/{volume_id}',
                                  rel=['hea-volume'])
        ],
        registry_docker_image=RealRegistryContainerConfig(HEASERVER_REGISTRY_IMAGE),
        exclude=['body_put'])
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._body_post:
            encoded = b64encode(b'Tritimus/').decode('utf-8')
            coll_key = get_collection_key_from_name(db_values, self._coll)
            modified_data = {**db_values[coll_key][0],
                             'display_name': 'Tritimus',
                             'actual_object_id': encoded,
                             'actual_object_uri': '/'.join(
                                 db_values[coll_key][0]['actual_object_uri'].split('/')[:-1] + [encoded]),
                             'name': encoded,
                             's3_uri': '/'.join(db_values[coll_key][0]['s3_uri'].split('/')[:-2] + ['Tritimus', '']),
                             'key': 'Tritimus/',
                             'path': '/arp-scale-2-cloud-bucket-with-tags11/Tritimus/'}
            if 'id' in modified_data:
                del modified_data['id']
            self._body_post = expectedvalues._create_template(modified_data)
