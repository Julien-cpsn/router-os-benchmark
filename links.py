from gns3fy import Gns3Connector, Node, Link
from loguru import logger


def link_nodes(gns3: Gns3Connector, project_id: str, router: Node, client: Node, server: Node):
    logger.info("Linking client to router")
    client_to_router_nodes = [
        { 'node_id': client.node_id, 'adapter_number': 0, 'port_number': 0 },
        { 'node_id': router.node_id, 'adapter_number': 0, 'port_number': 0 },
    ]
    client_to_router_link = Link(project_id=project_id, connector=gns3, nodes=client_to_router_nodes)
    client_to_router_link.create()

    logger.info("Linking server to router")
    server_to_router_nodes = [
        { 'node_id': server.node_id, 'adapter_number': 0, 'port_number': 0 },
        { 'node_id': router.node_id, 'adapter_number': 1, 'port_number': 0 },
    ]
    server_to_router_link = Link(project_id=project_id, connector=gns3, nodes=server_to_router_nodes)
    server_to_router_link.create()

    """
    server_to_client_nodes = [
        { 'node_id': server.node_id, 'adapter_number': 0, 'port_number': 0 },
        { 'node_id': client.node_id, 'adapter_number': 0, 'port_number': 0 },
    ]
    server_to_client_link = Link(project_id=project_id, connector=gns3, nodes=server_to_client_nodes)
    server_to_client_link.create()
    """
