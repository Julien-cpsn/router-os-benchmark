from gns3fy import Gns3Connector, Link
from loguru import logger

from src.types import Node, Test, DistantNetwork
from src.utils import network_from_ip, change_last_ip_class


def find_node(nodes: list[Node], name: str) -> Node:
    for node in nodes:
        if node.name == name:
            return node

    logger.error(f'Could not find node {name}')
    exit(1)

def link_nodes(gns3: Gns3Connector, project_id: str, nodes: list[Node], link: dict):
    node_a = find_node(nodes=nodes, name=link['node_a'])
    node_b = find_node(nodes=nodes, name=link['node_b'])
    adapter_a = link['adapter_a']
    adapter_b = link['adapter_b']

    logger.info(f"Linking {link['node_a']} to {link['node_b']}")
    nodes_to_link = [
        { 'node_id': node_a.gns3_node.node_id, 'adapter_number': adapter_a, 'port_number': 0 },
        { 'node_id': node_b.gns3_node.node_id, 'adapter_number': adapter_b, 'port_number': 0 },
    ]
    new_link = Link(project_id=project_id, connector=gns3, nodes=nodes_to_link)

    try:
        new_link.create()
    except Exception as e:
        logger.error(e)
        exit(1)

    node_a_ip = node_a.get_ip(adapter_a)
    node_b_ip = node_b.get_ip(adapter_b)

    if node_a.node_type == 'router':
        node_a.distant_networks.append(DistantNetwork(
            network=network_from_ip(node_b_ip),
            gateway=node_a_ip,
            adapter=adapter_a
        ))

    if node_b.node_type == 'router':
        node_b.distant_networks.append(DistantNetwork(
            network=network_from_ip(node_a_ip),
            gateway=node_b_ip,
            adapter=adapter_b
        ))


def generate_routes_from_test(tests: list[Test], nodes: list[Node]):
    logger.info('Generating routes from provided tests')

    for test in tests:
        from_node = find_node(nodes, test.from_node)
        to_node = find_node(nodes, test.to_node)

        if from_node.node_type == 'router' or to_node.node_type == 'router':
            logger.error('Cannot test from/to router nodes, only guests')
            exit(1)

        from_node.distant_networks.append(DistantNetwork(
            network=network_from_ip(to_node.ip),
            # Since guests only have one adapter, they are linked either to a router or another guest
            gateway=change_last_ip_class(from_node.ip, '1'),
            adapter=4
        ))

        to_node.distant_networks.append(DistantNetwork(
            network=network_from_ip(from_node.ip),
            # Since guests only have one adapter, they are linked either to a router or another guest
            gateway=change_last_ip_class(to_node.ip, '1'),
            adapter=4
        ))