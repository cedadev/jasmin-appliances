#!/usr/bin/python

# Copyright (c) 2019 STFC.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}


DOCUMENTATION = """
---
module: os_volume_upload_to_image
short_description: Uploads a bootable volume as an image.
version_added: "1.0"
author: "Matt Pryor"
description:
  - Uploads a bootable Cinder volume as a Glance image.
requirements:
  - "python >= 2.7"
  - "openstacksdk"
options:
  image_name:
    type: str
    description:
      - The name of the image to create.
    required: true
  volume_id:
    type: str
    description:
      - The ID of the volume to upload as an image.
    required: true
  force:
    type: bool
    description:
      - Force upload the volume even if it is currently attached.
    required: false
    default: false
  container_format:
    type: str
    description:
      - The container format for the new image.
    required: false
  disk_format:
    type: str
    description:
      - The disk format for the new image.
    required: false
  wait:
    type: bool
    description:
      - Wait for the image to become active before returning.
    required: false
    default: true
  timeout:
    type: int
    description:
      - If wait=true, the time in seconds to wait for the image to become active.
    required: false
    default: 120
extends_documentation_fragment: openstack
"""

EXAMPLES = """
- name: Upload volume as image
  os_volume_upload_to_image:
    image_name: "my-new-image"
    volume: "<volume-id>"
  register: result

- name: Show output
  debug: var=result.image_id
"""

RETURN = """
image_id:
    description: The ID of the created image.
    returned: success
    type: str
"""

import time
import traceback

from ansible.module_utils.basic import AnsibleModule
from openstack.cloud.plugins.module_utils.openstack import (
    openstack_cloud_from_module, openstack_full_argument_spec,
    openstack_module_kwargs)


class TimeoutError(RuntimeError):
    """
    Raised if the image creation times out.
    """


def main():
    argument_spec = openstack_full_argument_spec(
        image_name=dict(required=True, type="str"),
        volume_id=dict(required=True, type="str"),
        force=dict(default=False, type="bool"),
        container_format=dict(default=None, type="str"),
        disk_format=dict(default=None, type="str"),
        wait=dict(default=True, type="bool"),
        timeout=dict(default=120, type="int"),
    )
    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    sdk, cloud = openstack_cloud_from_module(module)
    try:
        wait = module.params["wait"]
        timeout = module.params["timeout"]
        image = cloud.block_storage.create_image(
            module.params["image_name"],
            module.params["volume_id"],
            module.params["force"],
            module.params["container_format"],
            module.params["disk_format"],
            # These variables are not used by the openstacksdk implementation as of 09/04/2019
            wait,
            timeout,
        )
        # Wait for the image to become active and the volume to become available again
        volume_id = module.params["volume_id"]
        if wait:
            start = time.time()
            while time.time() < start + timeout:
                image = cloud.image.get_image(image.id)
                volume = cloud.block_storage.get_volume(volume_id)
                if (
                    image.status.lower() == "active"
                    and volume.status.lower() == "available"
                ):
                    break
            else:
                raise TimeoutError("Timed out waiting for image.")
        module.exit_json(changed=True, image_id=image.id)
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == "__main__":
    main()
