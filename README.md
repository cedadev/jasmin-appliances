# jasmin-appliances

Appliances for use with JASMIN [Cluster-as-a-Service][caas] Project

## How to use this repository

Assuming that you are at the top of a checkout of this repository and a virtual
environment is available at `<path/to/venv>` created using
`--system-site-packages` flag to ensure `yum` dependencies are available to
Ansible, install all the `pip` dependencies (which may require you to
additionally install `python2-devel` and `gcc` packages through `yum`):

    $ virtualenv --system-site-packages <path/to/venv>
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

    $ ansible-playbook -i openstack.ini jasmin.yml -e @config/minimal.yml -e cluster_keypair=<keypair_name> -e cluster_name=<stack_name>

## Parameters to Provide

These playbooks may be invoked from an AWX context, or direct from the command line.

| Parameter | Notes |
|:----------|:------|
| `cluster_name` | The name of the cluster.  This is also the name of the Heat stack, and the stem for all instance names. |
| `cluster_state` | Can be one of present or absent, defaulting to present if not given. Determines whether the cluster should be created/updated (present) or deleted (absent). |
| `cluster_network` | The id or name of the network to which nodes should be attached. |
| `cluster_keypair` | The name of the keypair to inject into nodes. |
| `cluster_upgrade_system_packages` | Flag indicating whether system packages should be upgraded (i.e. the equivalent of yum update -y). Defaults to `false`. |
| `cluster_fixed_ip` | The fixed IP address of the floating IP to use when not using an ephemeral bastion. |

When invoked via AWX, OpenStack configuration parameters are supplied.
From the command line these can be drawn in from the user environment by sourcing
extra vars from `config/auth.yml`, for example:

```
$ ansible-playbook -i inventory nfs-infra.yml \
    -e cluster_name=stig-nfs \
    -e cluster_keypair=oneswig \
    -e cluster_network="caastest-U-internal" \
    -e cluster_fixed_ip=192.171.139.120 \
    -e @config/auth.yml
```

## Backing up and restoring AWX configuration using tower-cli

To backup:

    tower-cli receive --all > awx/backup.json

To restore:

    tower-cli send awx/backup.json

[caas]: https://github.com/cedadev/jasmin-cluster-as-a-service/projects/1
