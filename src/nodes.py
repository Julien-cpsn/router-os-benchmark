from gns3fy import Gns3Connector, Node
from loguru import logger


def create_node(gns3: Gns3Connector, project_id: str, name: str, template: str, x = 0, y = 0) -> Node:
    logger.info(f"Creating node {name}")
    node = Node(project_id=project_id, connector=gns3, name=name, template=template, x=x, y=y)
    node.create()

    return node
