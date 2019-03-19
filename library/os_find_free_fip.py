#!/usr/bin/python

# Copyright (c) 2019 STFC.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: os_find_free_fip
short_description: Finds (or allocates) and returns an unattached floating IP.
version_added: "1.0"
author: "Matt Pryor"
description:
    - Attempts to find an unused floating IP from those already allocated.
      If one cannot be found, attempts to allocate a new one.
requirements:
    - "python >= 2.7"
    - "openstacksdk"
options:
    floating_network_id:
        type: str
        description:
          - The ID of the network that provides floating IPs
        required: true
extends_documentation_fragment: openstack
'''

EXAMPLES = '''
- name: Get a floating IP to use
  os_find_free_fip:
    cloud: rax-dfw
    floating_network_id: netid
  register: result

- name: Show output
  debug: var=result.floating_ip_id
- debug: var=result.floating_ip_address
'''

RETURN = '''
floating_ip_id:
    description: The ID of the floating IP.
    returned: success
    type: str
floating_ip_address:
    description: The IP address of the floating IP.
    returned: success
    type: str
'''

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module


def main():

    argument_spec = openstack_full_argument_spec(
        floating_network_id = dict(required=True)
    )
    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    sdk, cloud = openstack_cloud_from_module(module)
    try:
        # First, try to find a free floating IP
        fip = cloud.network.find_available_ip()
        # If that failed, try to allocate one
        if fip is None:
            fip = cloud.network.create_ip(
                floating_network_id = module.params['floating_network_id']
            )
        # Return the IP details
        module.exit_json(
            changed = True,
            floating_ip_id = fip.id,
            floating_ip_address = fip.floating_ip_address
        )
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()

