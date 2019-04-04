import os

import openstack as sdk
import shortuuid

SSH_DIR = './jasmin_ssh'


def delete_keypair(conn, keypair):
    conn.compute.delete_keypair(keypair)
#    keypair_path = "%s/%s" % (SSH_DIR, keypair.name)
#    os.remove(keypair_path)


def create_keypair(conn):
    keypair_name = 'test-%s' % shortuuid.uuid()
    keypair = conn.compute.find_keypair(keypair_name)

    if not keypair:
        with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as f:
            pubkey = f.read()
        keypair = conn.create_keypair(name=keypair_name, public_key=pubkey)

#        try:
#            os.mkdir(SSH_DIR)
#        except OSError as e:
#            if e.errno != errno.EEXIST:
#                raise e
#
#        keypair_path = "%s/%s" % (SSH_DIR, keypair_name)
#        with open(keypair_path, 'w') as f:
#            f.write("%s" % keypair.private_key)
#        os.chmod(keypair_path, 0o400)

    return keypair


def create_connection():
    return sdk.connect()
