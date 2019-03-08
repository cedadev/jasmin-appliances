#!/usr/bin/env python
#
# Copyright (c) 2019 StackHPC Ltd.
# Apache 2 Licence

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: os_stack_outputs
short_description: Retrieve stack outputs
author: pierre@stackhpc.com
version_added: "1.0"
description:
    - Retrieve outputs from stacks using OpenStack Heat API.
notes:
    - This module creates a new top-level C(stack_outputs) fact, which
      contains a list of stack outputs.
requirements:
    - "python >= 2.6"
    - "openstacksdk"
    - "python-heatclient"
options:
   cloud:
     description:
       - Cloud name inside cloud.yaml file.
     type: str
   stack_id:
     description:
        - Heat stack name or uuid.
     type: str
extends_documentation_fragment: openstack
'''

EXAMPLES = '''
# Gather outputs from <stack_id>:
- os_stack_outputs:
    cloud: mycloud
    stack_id: xxxxx-xxxxx-xxxx-xxxx
- debug:
    var: stack_outputs
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.utils.display import Display
from heatclient.client import Client
import openstack

display = Display()

class OpenStackAuthConfig(Exception):
    pass

class StackOutputs(object):
    def __init__(self, **kwargs):
        self.stack_id = kwargs['stack_id']
        self.connect(**kwargs)

    def connect(self, **kwargs):
        if kwargs['auth_type'] == 'environment':
            self.cloud = openstack.connect()
        elif kwargs['auth_type'] == 'cloud':
            self.cloud = openstack.connect(cloud=kwargs['cloud'])
        elif kwargs['auth_type'] == 'password':
            self.cloud = openstack.connect(**kwargs['auth'])
        else:
            raise OpenStackAuthConfig('Provided auth_type must be one of [environment, cloud, password].')

        self.client = Client('1', session=self.cloud.session)

    def get(self):
        result = dict()
        stack = self.client.stacks.get(self.stack_id)
        for item in stack.outputs:
            result[item['output_key']] = item['output_value']
        return result

if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec = dict(
            cloud=dict(required=False, type='str'),
            auth=dict(required=False, type='dict'),
            auth_type=dict(default='environment', required=False, type='str'),
            stack_id=dict(required=True, type='str'),
        ),
        supports_check_mode=False
    )

    display = Display()

    try:
        stack_outputs = StackOutputs(**module.params)
    except Exception as e:
        module.fail_json(repr(e))
    module.exit_json(changed=False,ansible_facts=dict(stack_outputs=stack_outputs.get()))
