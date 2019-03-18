# jasmin-appliances

Appliances for use with JASMIN Cluster-as-a-Service Project

## How to use this repository

Assuming that you are at the top of a checkout of this repository and a virtual
environment is available at <venv>, install all the dependencies:

    $ source <path/to/venv>/bin/activate
    $ pip install -r requirements.txt
    $ ansible-galaxy install -p roles -r roles/requirements.yml

Configure the environment with OpenStack variables:

    $ . <path/to/openrc>

Make sure you have a public key uploaded to OpenStack:

    $ openstack keypair list

Launch a cluster by calling the jasmin.yml playbook, passing a config file as
Ansible extra variables, providing a keypair to use to connect to the cluster,
and assigning a unique name to the cluster (which will be used to name the
stack). For example:

    $ ansible-playbook -i inventory jasmin.yml -e @config/minimal.yml -e cluster_keypair=<keypair_name> -e cluster_name=<stack_name>

## Parameters to Provide

These playbooks may be invoked from an AWX context, or direct from the command line.


| `cluster_name` | The name of the cluster.  This is also the name of the Heat stack, and the stem for all instance names. |
| `cluster_state` | Can be one of present or absent, defaulting to present if not given. Determines whether the cluster should be created/updated (present) or deleted (absent). |
| `cluster_network` | The id or name of the network to which nodes should be attached. |
| `cluster_keypair` | The name of the keypair to inject into nodes. |
| `cluster_upgrade_system_packages` | Flag indicating whether system packages should be upgraded (i.e. the equivalent of yum update -y). Defaults to `false`. |
| `cluster_fip_uuid` | The UUID of a floating IP (allocated to the project but currently unassociated).  This will be used for the bastion host, which could be transient. |
| `cluster_fip_ip` | The IP address of the floating IP to use. |

...
