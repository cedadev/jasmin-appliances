import pytest
import shortuuid

import tests.utils.ansible as ansible_utils
import tests.utils.os_utils as os_utils

class SlurmCluster(object):
    def __init__(self, cluster_name, cluster_fixed_ip, ansible_return_code):
        self.cluster_name = cluster_name
        self.cluster_fixed_ip = cluster_fixed_ip
        self.ansible_return_code = ansible_return_code

@pytest.fixture(scope="module")
def slurm_cluster(keypair, storage_cluster):
    conn = os_utils.create_connection()
    fip = conn.network.find_available_ip()
    cluster_fixed_ip = fip.floating_ip_address
    cluster_name = 'test-slurm-{}'.format(shortuuid.uuid())
    extra_vars = {
        'cluster_fixed_ip': cluster_fixed_ip,
        'cluster_keypair': keypair,
        'cluster_name': cluster_name,
        'cluster_network': 'caastest-U-internal',
        'cluster_state': 'present',
        'cluster_upgrade_system_packages': 'false',
        'storage_name': storage_cluster.cluster_name,
        'validation': 'true',
    }
    return_code = ansible_utils.run_playbook('slurm-infra.yml',
                                             extra_vars=extra_vars)
    yield SlurmCluster(cluster_name, cluster_fixed_ip, return_code)
    extra_vars['cluster_state'] = 'absent'
    ansible_utils.run_playbook('slurm-infra.yml', extra_vars=extra_vars)

def test_slurm_validation(slurm_cluster):
    assert slurm_cluster.ansible_return_code == 0
