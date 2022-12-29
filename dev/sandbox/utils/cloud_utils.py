import time
from typing import Tuple, Dict, Any

import munch
import openstack
import openstack.exceptions
import configparser

from src import exception
from src.log import globalLog


CONFIG = configparser.ConfigParser()['DEFAULT']


def _cloud_connection() -> openstack.connection.Connection:
    return openstack.connection.from_config()


def _server_attrs(conn: openstack.connection.Connection) -> Dict[str, Any]:
    image = conn.compute.find_image(CONFIG["IMAGE_NAME"])
    flavor = conn.compute.find_flavor(CONFIG["FLAVOR_NAME"])
    network = conn.network.find_network(CONFIG["NETWORK_NAME"])
    keypair = conn.compute.find_keypair(CONFIG["KEYPAIR_NAME"])

    if image is None or flavor is None \
            or network is None or keypair is None:
        raise exception.CloudException('Could not find instance attrs in cloud')

    return {
        "name": CONFIG["INSTANCE_NAME"],
        "image": image.id,
        "flavor": flavor.name,
        "network": network,
        "key_name": keypair.name,
        "wait": True,
        "ip_pool": CONFIG["IP_POOL_NAME"]
    }


def _create_instance(conn: openstack.connection.Connection) -> munch.Munch:
    try:
        server_attrs = _server_attrs(conn)
        server = conn.create_server(**server_attrs)
    except openstack.exceptions.OpenStackCloudException as exc:
        globalLog.error(exc)
        raise exception.CloudException("Failed to create instance")
    return server


def setup_instance() -> Tuple[str, str]:
    sleep_sec = 60

    with _cloud_connection() as conn:
        server = conn.get_server(CONFIG["INSTANCE_NAME"])
        if server is None:
            globalLog.debug("Instance was not found, creating instance")
            server = _create_instance(conn)
        else:
            globalLog.debug("Instance was found, rebuilding instance")
            server = conn.rebuild_server(server_id=server.id, image_id=server.image.id, wait=True)
        globalLog.debug(f"Sleeping for {sleep_sec}s")
        time.sleep(sleep_sec)

    return server.public_v4, CONFIG["USER_NAME"]


def delete_instance() -> None:
    with _cloud_connection() as conn:
        server = conn.compute.find_server(CONFIG["INSTANCE_NAME"])
        if server is not None:
            conn.delete_server(server.id)
