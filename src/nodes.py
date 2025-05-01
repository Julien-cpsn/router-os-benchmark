from typing import Optional

from gns3fy import Gns3Connector, Node
from loguru import logger

def create_node(gns3: Gns3Connector, template_prefix: str, project_id: str, node_name: str, os_name: Optional[str], x = 0, y = 0) -> Node:
    logger.info('Creating node')

    if os_name is not None:
        template_name = f'{template_prefix} {os_name} {node_name}'
    else:
        template_name = f'{template_prefix} {node_name}'

    node = Node(project_id=project_id, connector=gns3, name=node_name, template=template_name, x=x, y=y)
    node.create()

    return node
