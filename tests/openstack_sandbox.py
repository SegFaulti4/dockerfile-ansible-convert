import openstack


IMAGE_NAME = "Ubuntu Server 18.04 LTS (Bionic Beaver)"
FLAVOR_NAME = "Standard2.small.s10"
NETWORK_NAME = "net-for-intra-sandbox"
KEYPAIR_NAME = "popov_git_ssh"


def main():
    conn = openstack.connection.from_config()

    image = conn.compute.find_image(IMAGE_NAME)
    flavor = conn.compute.find_flavor(FLAVOR_NAME)
    network = conn.network.find_network(NETWORK_NAME)
    keypair = conn.compute.find_keypair(KEYPAIR_NAME)
    # ip_pools = {pool['name']: pool for pool in conn.list_floating_ip_pools()}

    server_attrs = {
        "name": "popov-ansible-test",
        "image_id": image.id,
        "flavor_id": flavor.id,
        "networks": [{"uuid": network.id}],
        "key_name": keypair.name,
        "ip_pool": "ispras"
    }
    server = conn.compute.create_server(**server_attrs)
    status = conn.wait_for_server(server)


if __name__ == '__main__':
    main()
