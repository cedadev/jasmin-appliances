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
options:
   cloud:
     description:
       - Cloud name inside cloud.yaml file.
     type: str
   stack:
     description:
        - Heat stack name or uuid.
     type: str
extends_documentation_fragment: openstack
'''

EXAMPLES = '''
# Gather outputs from <stack> name or id:
- os_stack_outputs:
    cloud: mycloud
    stack: xxxxx-xxxxx-xxxx-xxxx
- debug:
    var: stack_outputs
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import (openstack_full_argument_spec,
                                            openstack_module_kwargs,
                                            openstack_cloud_from_module)

def main():

    argument_spec = openstack_full_argument_spec(
        stack=dict(required=True),
    )
    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    sdk, cloud = openstack_cloud_from_module(module)
    try:
        result = dict()
        stack = cloud.get_stack(module.params['stack'])
        if stack:
            for item in stack.outputs:
                result[item['output_key']] = item['output_value']
        else:
            raise sdk.exceptions.OpenStackCloudException(
                'Stack {} not found.'.format(module.params['stack']))
        module.exit_json(changed=False,
            ansible_facts=dict(openstack_stack_outputs=result))

    except sdk.exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
