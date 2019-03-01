#!/usr/bin/python

# Copyright (c) 2019 StackHPC Ltd.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: os_keystone_trust
short_description: Retrieve an auth token
version_added: "1.0"
author: "Bharat Kunwar (@brtknr)"
description:
    - Retrieve an auth token from an OpenStack Cloud
requirements:
    - "python >= 2.7"
    - "openstacksdk"
options:
  impersonation:
    type: bool
    description:
      - Whether the trustee should impersonate the current user
    required: false
    default: true
  trustee_user_id:
    type: str
    description:
      - Whether the trustee should impersonate the current user
    required: true
  roles:
    type: list
    description:
      - List of roles dict to delegate, the key must be a role `id` or `name`.
    required: true
extends_documentation_fragment: openstack
'''

EXAMPLES = '''
- name: Authenticate to the cloud and retrieve the service catalog
  os_keystone_trust:
    cloud: rax-dfw
    impersonation: true
    trustee_user_id: abc123
    roles:
      - name: _member_

- name: Show output
  debug: var=trust_id
- debug: var=trustor_user_id
- debug: var=project_id
- debug: var=auth_token
'''

RETURN = '''
trust_id:
    description: Openstack Trust ID
    returned: success
    type: str
trustor_user_id:
    description: Openstack Trustor User ID
    returned: success
    type: str
project_id:
    description: Openstack Project ID
    returned: success
    type: str
auth_token:
    description: Openstack API Auth Token
    returned: success
    type: str
'''

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module


def main():

    argument_spec = openstack_full_argument_spec(
        trustee_user_id=dict(required=True),
        roles=dict(required=True, type='list'),
        impersonation=dict(default=True, type='bool')
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    trustee_user_id = module.params['trustee_user_id']
    impersonation = module.params['impersonation']
    roles = module.params['roles']

    sdk, cloud = openstack_cloud_from_module(module)
    try:
        project_id = cloud.current_project.id
        trustor_user_id = cloud.current_user_id
        trust = cloud.identity.create_trust(
            trustor_user_id=trustor_user_id,
            trustee_user_id=trustee_user_id,
            project_id=project_id,
            impersonation=impersonation,
            roles=roles
        )
        module.exit_json(
            changed=True,
            ansible_facts=dict(
                trust_id=trust.id,
                trustor_user_id=trustor_user_id,
                project_id=project_id,
                auth_token=cloud.auth_token
            )
        )
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()

