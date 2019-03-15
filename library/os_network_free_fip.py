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
module: os_network_fip
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
    ip:
        type: str
        description:
          - The IP address that is required. If the IP is already attached, the
            module will attempt to free it from the attached port.
        required: false
extends_documentation_fragment: openstack
'''

EXAMPLES = '''
- name: Get a floating IP to use
  os_network_free_fip:
    cloud: rax-dfw
    floating_network_id: netid
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
        floating_network_id = dict(required=True),
        ip = dict(default=None)
    )
    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    sdk, cloud = openstack_cloud_from_module(module)
    try:
        fip_ip = module.params['ip']
        floating_network_id = cloud.network.find_network(module.params['floating_network_id']).id
        changed = False
        if fip_ip:
            # This is when a specific floating IP is requested
            fip = cloud.network.find_ip(fip_ip,
                    floating_network_id=floating_network_id
                )
            if fip is None:
                raise ValueError(
                    "Requested floating IP {} not found on network {}.".format(fip_ip, floating_network_id))
            else:
                # Attemps to detach from existing port only if already assigned
                if fip.port_id is not None:
                    fip = cloud.network.remove_ip_from_port(fip)
                    changed = True
        else:
            # First, try to find a free floating IP
            fip = cloud.network.find_available_ip(
                    floating_network_id=floating_network_id
                )
            # If that failed, try to allocate one
            if fip is None:
                fip = cloud.network.create_ip(
                    floating_network_id=floating_network_id 
                )
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

