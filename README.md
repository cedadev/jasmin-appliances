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
Ansible extra variables, and providing a keypair to use to connect to the
cluster. For example:

    $ ansible-playbook -i inventory jasmin.yml -e @config/minimal.yml -e cluster_keypair=<keypair_name>
