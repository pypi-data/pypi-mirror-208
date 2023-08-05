"""
Creates a test case class for use with the unittest library that is built into Python.
"""
from heaserver.service.testcase import expectedvalues
from heaserver.service.testcase.awss3microservicetestcase import get_test_case_cls_default
from heaserver.service.testcase.collection import CollectionKey, get_collection_key_from_name
from heaserver.bucket import service
from heaserver.service.testcase.mockaws import MockS3Manager
from heaserver.service.testcase.dockermongo import DockerMongoManager, RealRegistryContainerConfig
from heaserver.service.testcase.testenv import MicroserviceContainerConfig
from heaobject.user import NONE_USER
from heaobject.registry import Resource
from heaobject.volume import DEFAULT_FILE_SYSTEM
from heaserver.service.testcase.expectedvalues import Action

db_store = {
    CollectionKey(name=service.MONGODB_BUCKET_COLLECTION, db_manager_cls=MockS3Manager): [{
        'id': 'hci-foundation-1',
        'created': '2022-05-17T00:00:00+00:00',
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'object_count': None,
        'size': None,
        'display_name': 'hci-foundation-1',
        'invites': [],
        'modified': None,
        'name': 'hci-foundation-1',
        'owner': NONE_USER,
        'shares': [],
        'source': 'AWS Simple Cloud Storage (S3)',
        'type': 'heaobject.bucket.AWSBucket',
        'arn': 'arn:aws:s3::hci-foundation-1',
        'versioned': True,
        'encrypted': False,
        'region': 'us-west-1',
        'permission_policy': None,
        'tags': [],
        's3_uri': 's3://hci-foundation-1/',
        'presigned_url': None,
        'locked': False,
        'mime_type': 'application/x.awsbucket',
        'bucket_id': 'hci-foundation-1'
    },
        {
            'id': 'hci-foundation-2',
            'created': '2022-05-17T00:00:00+00:00',
            'derived_by': None,
            'derived_from': [],
            'description': None,
            'object_count': None,
            'size': None,
            'display_name': 'hci-foundation-2',
            'invites': [],
            'modified': None,
            'name': 'hci-foundation-2',
            'owner': NONE_USER,
            'shares': [],
            'source': 'AWS Simple Cloud Storage (S3)',
            'type': 'heaobject.bucket.AWSBucket',
            'arn': 'arn:aws:s3::hci-foundation-2',
            'versioned': True,
            'encrypted': False,
            'region': 'us-west-1',
            'permission_policy': None,
            'tags': [],
            's3_uri': 's3://hci-foundation-2/',
            'presigned_url': None,
            'locked': False,
            'mime_type': 'application/x.awsbucket',
        'bucket_id': 'hci-foundation-2'
        }

    ],
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
        'owner': NONE_USER,
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
        'owner': NONE_USER,
        'shared_with': [],
        'source': None,
        'type': 'heaobject.volume.Volume',
        'version': None,
        'file_system_name': 'amazon_web_services',
        'credential_id': None  # Let boto3 try to find the user's credentials.
    }]}

HEASERVER_REGISTRY_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-registry:1.0.0a32'
HEASERVER_VOLUMES_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-volumes:1.0.0a17'
volume_microservice = MicroserviceContainerConfig(image=HEASERVER_VOLUMES_IMAGE, port=8080, check_path='/volumes',
                                                  resources=[Resource(resource_type_name='heaobject.volume.Volume',
                                                                      base_path='/volumes',
                                                                      file_system_name=DEFAULT_FILE_SYSTEM),
                                                             Resource(resource_type_name='heaobject.volume.FileSystem',
                                                                      base_path='/filesystems',
                                                                      file_system_name=DEFAULT_FILE_SYSTEM)],
                                                  db_manager_cls=DockerMongoManager)


def get_test_case_cls(*args, **kwargs):
    """Get a test case class specifically for this microservice."""

    class MyTestCase(get_test_case_cls_default(*args, **kwargs)):
        def __init__(self, *args_, **kwargs_):
            super().__init__(*args_, **kwargs_)
            if self._body_post:
                modified_data = {**db_store[get_collection_key_from_name(db_store, self._coll)][0], 'name': 'tritimus',
                                 'display_name': 'tritimus', 's3_uri': 's3://tritimus/', 'bucket_id': 'tritimus',
                                 'versioned': False, 'arn': 'arn:aws:s3::tritimus'}
                if 'id' in modified_data:
                    del modified_data['id']
                self._body_post = expectedvalues._create_template(modified_data)

    return MyTestCase


TestCase = \
    get_test_case_cls(coll=service.MONGODB_BUCKET_COLLECTION,
                      wstl_package=service.__package__,
                      href='http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/',
                      fixtures=db_store,
                      db_manager_cls=MockS3Manager,
                      get_actions=[Action(name='heaserver-buckets-bucket-get-properties',
                                          rel=['hea-properties', 'hea-context-menu']),
                                   Action(name='heaserver-buckets-bucket-get-open-choices',
                                          url='http://localhost:8080/volumes/{volume_id}/buckets/{id}/opener',
                                          rel=['hea-opener-choices', 'hea-context-menu']),
                                   Action(name='heaserver-buckets-bucket-get-self',
                                          url='http://localhost:8080/volumes/{volume_id}/buckets/{id}',
                                          rel=['self']),
                                   Action(name='heaserver-buckets-bucket-get-volume',
                                          url='http://localhost:8080/volumes/{volume_id}',
                                          rel=['hea-volume']),
                                   Action(name='heaserver-buckets-bucket-get-awsaccount',
                                          url='http://localhost:8080/volumes/{volume_id}/awsaccounts/me',
                                          rel=['hea-account']),
                                   Action(name='heaserver-buckets-bucket-get-create-choices',
                                          url='http://localhost:8080/volumes/{volume_id}/buckets/{id}/creator',
                                          rel=['hea-creator-choices', 'hea-context-menu']),
                                   Action(name='heaserver-buckets-bucket-get-trash',
                                          url='http://localhost:8080/volumes/{volume_id}/awss3trash',
                                          rel=['hea-trash', 'hea-context-menu'])
                                   ],
                      get_all_actions=[Action(name='heaserver-buckets-bucket-get-properties',
                                              rel=['hea-properties', 'hea-context-menu']),
                                       Action(name='heaserver-buckets-bucket-get-open-choices',
                                              url='http://localhost:8080/volumes/{volume_id}/buckets/{id}/opener',
                                              rel=['hea-opener-choices', 'hea-context-menu']),
                                       Action(name='heaserver-buckets-bucket-get-self',
                                          url='http://localhost:8080/volumes/{volume_id}/buckets/{id}',
                                          rel=['self']),
                                       Action(name='heaserver-buckets-bucket-get-create-choices',
                                          url='http://localhost:8080/volumes/{volume_id}/buckets/{id}/creator',
                                          rel=['hea-creator-choices', 'hea-context-menu']),
                                       Action(name='heaserver-buckets-bucket-get-trash',
                                          url='http://localhost:8080/volumes/666f6f2d6261722d71757578/awss3trash',
                                          wstl_url='http://localhost:8080/volumes/{volume_id}/awss3trash',
                                          rel=['hea-trash', 'hea-context-menu'])],
                      duplicate_action_name='',
                      exclude=['body_put'],
                      registry_docker_image=RealRegistryContainerConfig(HEASERVER_REGISTRY_IMAGE),
                      other_docker_images=[volume_microservice])
