import pytest
import shortuuid

import tests.utils.ansible as ansible_utils
import tests.utils.os_utils as os_utils

@pytest.fixture(scope="module")
def keypair():
    conn = os_utils.create_connection()
    keypair = os_utils.create_keypair(conn)
    yield keypair.name
    os_utils.delete_keypair(conn, keypair)

class StorageCluster(object):
    def __init__(self, storage_type, cluster_name):
        self.storage_type = storage_type
        self.cluster_name = cluster_name

@pytest.fixture(scope="module",
                params=["nfs", "gluster", "beegfs"])
def storage_cluster(request, keypair):
    cluster_name = 'test-{}-{}'.format(request.param, shortuuid.uuid())
    extra_vars = {
        'cluster_keypair': keypair,
        'cluster_name': cluster_name,
        'cluster_network': 'caastest-U-internal',
        'cluster_state': 'present',
        'cluster_upgrade_system_packages': 'false',
    }
    ansible_utils.run_playbook('{}-infra.yml'.format(request.param),
                               extra_vars=extra_vars)
    yield StorageCluster(request.param, cluster_name)
    extra_vars['cluster_state'] = 'absent'
    ansible_utils.run_playbook('{}-infra.yml'.format(request.param),
                               extra_vars=extra_vars)
