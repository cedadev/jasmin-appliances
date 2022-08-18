#!/usr/bin/python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: keycloak_component

short_description: Create, update or delete a Keycloak component

author: "Matt Pryor"

requirements:
    - "python >= 2.7"

options:
  realm:
    type: string
    description:
      - The realm in which the component should live
    required: false
    default: master

  name:
    type: string
    description:
      - The name of the component
    required: true

  state:
    description:
      - The state of the component
      - On C(present), the component will be created (or updated if it exists already).
      - On C(absent), the component will be removed if it exists.
    choices: ['present', 'absent']
    default: 'present'

  provider_type:
    type: string
    description:
      - The Keycloak provider type
    required: true

  provider_id:
    type: string
    description:
      - The Keycloak provider ID
    required: false

  subtype:
    type: string
    description:
      - The Keycloak component subtype
    required: false

  parent_id:
    type: string
    description:
      - The ID of the parent component
    required: false

  config:
    description:
      - Dict specifying the configuration options for the component
    required: false

extends_documentation_fragment: keycloak
'''

import json
import traceback

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.keycloak import (KeycloakAPI, get_token,
                                           keycloak_argument_spec)
from ansible.module_utils.six import string_types
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.urls import open_url

URL_COMPONENTS = "{url}/admin/realms/{realm}/components"
URL_COMPONENT = URL_COMPONENTS + "/{id}"


def make_request(api, url, method = 'GET', msg = '{}', **params):
    """
    Context manager for making requests
    """
    try:
        return open_url(
            url, method = method,
            headers = api.restheaders,
            validate_certs = api.validate_certs,
            **params
        )
    except Exception as e:
        api.module.fail_json(msg = msg.format(str(e)), exception = traceback.format_exc())


def get_component(api, realm, name, provider_type, parent_id = None):
    """
    Gets the first component that matches the given params, or None if
    one does not exist.
    """
    params = dict(name = name, type = provider_type)
    if parent_id is not None:
        params.update(parent = parent_id)
    try:
        return json.load(
            make_request(
                api,
                (URL_COMPONENTS + '?{query}').format(
                    url = api.baseurl,
                    realm = realm,
                    query = urlencode(params)
                ),
                msg = "Could not obtain list of components: {}"
            )
        )[0]
    except IndexError:
        return None
    except ValueError as e:
        api.module.fail_json(
            msg = 'API returned incorrect JSON: {}'.format(str(e)),
            exception = traceback.format_exc()
        )


def create_component(api, realm, component):
    """
    Creates a component with the given parameters.
    """
    make_request(
        api,
        URL_COMPONENTS.format(url = api.baseurl, realm = realm),
        method = 'POST',
        data = json.dumps(component),
        msg = "Could not create component: {}"
    )


def update_component(api, realm, cid, component):
    """
    Updates the component with the given id with the given parameters.
    """
    make_request(
        api,
        URL_COMPONENT.format(url = api.baseurl, realm = realm, id = cid),
        method = 'PUT',
        data = json.dumps(component),
        msg = "Could not update component: {}"
    )


def delete_component(api, realm, cid):
    """
    Deletes the component with the given id.
    """
    make_request(
        api,
        URL_COMPONENT.format(url = api.baseurl, realm = realm, id = cid),
        method = 'DELETE',
        msg = "Could not delete component: {}"
    )


def to_list(value):
    if isinstance(value, Iterable) and not isinstance(value, string_types):
        return list(value)
    else:
        return [value]


def main():
    argument_spec = keycloak_argument_spec()
    argument_spec.update(
        realm = dict(type = 'str', default = 'master'),
        state = dict(default = 'present', choices = ['present', 'absent']),
        name = dict(type = 'str', required = True),
        provider_type = dict(type = 'str', required = True),
        provider_id = dict(type = 'str'),
        subtype = dict(type = 'str'),
        parent_id = dict(type = 'str'),
        config = dict(type = 'dict')
    )

    module = AnsibleModule(argument_spec = argument_spec, supports_check_mode = True)

    # Reuse existing code to authenticate with Keycloak
    api = KeycloakAPI(module, get_token(module.params))

    realm = module.params['realm']

    existing = get_component(
        api,
        realm,
        name = module.params['name'],
        provider_type = module.params['provider_type'],
        parent_id = module.params.get('parent_id')
    )

    if module.params['state'] == 'present':
        # Merge previous state with the given params to get the target state
        component = dict(
            existing or {},
            name = module.params['name'],
            providerType = module.params['provider_type']
        )
        provider_id = module.params.get('provider_id')
        if provider_id:
            component['providerId'] = provider_id
        subtype = module.params.get('subtype')
        if subtype:
            component['subType'] = subtype
        parent_id = module.params.get('parent_id')
        if parent_id:
            component['parentId'] = parent_id
        # Config is a dict, which we want to merge separately
        # The items in config also need to be lists, so convert any scalar values
        # and make sure any iterables are actually lists
        config = module.params.get('config', {})
        if config:
            merged_config = dict((existing or {}).get('config', {}))
            merged_config.update(module.params['config'])
            component['config'] = {
                k: to_list(v)
                for k, v in merged_config.items()
            }

        if not module.check_mode:
            if existing is None:
                create_component(api, realm, component)
            else:
                update_component(api, realm, component.pop('id'), component)

        # Get the new state of the component
        current = get_component(
            api,
            realm,
            name = component['name'],
            provider_type = component['providerType'],
            parent_id = component.get('parentId')
        )

        return module.exit_json(
            changed = (current != existing),
            component = current
        )
    else:
        if existing is None:
            module.exit_json(changed = False)
        if not module.check_mode:
            delete_component(api, realm, existing['id'])
        module.exit_json(changed = True)


if __name__ == '__main__':
    main()
