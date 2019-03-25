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
module: os_network_find_fip
short_description: Finds (or allocates) and returns a floating IP.
version_added: "1.0"
author: "Matt Pryor"
description:
  - If ip is given, attempt to find and return that IP.
  - If ip is not given, attempt to find an unused floating IP from those
    already allocated to the project. If one cannot be found, attempt
    to allocate a new one.
requirements:
  - "python >= 2.7"
  - "openstacksdk"
options:
  floating_network:
    type: str
    description:
      - The ID or name of the network that provides floating IPs.
    required: true
  ip:
    type: str
    description:
      - The IP address that is required.
    required: false
extends_documentation_fragment: openstack
'''

EXAMPLES = '''
- name: Get a floating IP to use
  os_network_find_fip:
    cloud: rax-dfw
    floating_network: netname
  register: result

- name: Show output
  debug: var=result.fip_id
- debug: var=result.fip_ip
'''

RETURN = '''
fip_id:
    description: The ID of the floating IP.
    returned: success
    type: str
fip_ip:
    description: The IP address of the floating IP.
    returned: success
    type: str
'''

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module


def main():

    argument_spec = openstack_full_argument_spec(
        floating_network = dict(required=True, type='str'),
        ip = dict(default=None, type='str'),
    )
    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    sdk, cloud = openstack_cloud_from_module(module)
    try:
        floating_network = module.params['floating_network']
        floating_network_id = cloud.network.find_network(floating_network).id
        fip_ip = module.params['ip']
        changed = False
        if fip_ip:
            # This is when a specific floating IP is requested
            fip = cloud.network.find_ip(fip_ip, floating_network_id = floating_network_id)
            if fip is None:
                raise ValueError(
                    "Floating IP {} not found on network {}.".format(fip_ip, floating_network)
                )
        else:
            # First, try to find a free floating IP
            fip = cloud.network.find_available_ip()
            # If that failed, try to allocate one
            if fip is None:
                fip = cloud.network.create_ip(floating_network_id = floating_network_id)
                changed = True
        # Return the IP details
        module.exit_json(
            changed = changed,
            fip_id = fip.id,
            fip_ip = fip.floating_ip_address
        )
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
