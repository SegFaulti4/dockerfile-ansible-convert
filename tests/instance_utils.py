import os
import time

import openstack
import openstack.exceptions

import docker2ansible.exception
from docker2ansible.log import globalLog


IMAGE_NAME = "Ubuntu Server 18.04 LTS (Bionic Beaver)"
FLAVOR_NAME = "Standard2.small.s10"
NETWORK_NAME = "net-for-intra-sandbox"
KEYPAIR_NAME = "popov_git_ssh"
IP_POOL_NAME = "ispras"
INSTANCE_NAME = "popov-ansible-test"


def _cloud_connection():
    return openstack.connection.from_config()


def _server_attrs(conn):
    image = conn.compute.find_image(IMAGE_NAME)
    flavor = conn.compute.find_flavor(FLAVOR_NAME)
    network = conn.network.find_network(NETWORK_NAME)
    keypair = conn.compute.find_keypair(KEYPAIR_NAME)

    if image is None or flavor is None \
            or network is None or keypair is None:
        raise docker2ansible.exception.CloudException('Could not find instance attrs in cloud')

    return {
        "name": INSTANCE_NAME,
        "image": image.id,
        "flavor": flavor.name,
        "network": network,
        "key_name": keypair.name,
        "wait": True,
        "ip_pool": IP_POOL_NAME
    }


def _create_instance(conn):
    try:
        server_attrs = _server_attrs(conn)
        server = conn.create_server(**server_attrs)
    except openstack.exceptions.OpenStackCloudException as exc:
        globalLog.error(exc)
        raise docker2ansible.exception.CloudException("Failed to create instance")
    return server


def _update_inventory(server):
    with open("inventory", "w") as outF:
        outF.writelines(["[dummy]\n", server.public_v4 + " ansible_ssh_user=ubuntu"])


def setup_instance():
    with _cloud_connection() as conn:
        server = conn.get_server(INSTANCE_NAME)
        if server is None:
            globalLog.debug("Instance was not found, creating instance")
            server = _create_instance(conn)
        else:
            globalLog.debug("Instance was found, rebuilding instance")
            server = conn.rebuild_server(server_id=server.id, image_id=server.image.id, wait=True)
        globalLog.debug("Updating inventory in " + os.getcwd() + '/inventory')
        _update_inventory(server)
        globalLog.debug("Sleeping for 60s")
        time.sleep(60)


def destroy_instance():
    with _cloud_connection() as conn:
        server = conn.compute.find_server(INSTANCE_NAME)
        if server is not None:
            conn.delete_server(server.id)
