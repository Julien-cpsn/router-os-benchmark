from typing import Optional

from gns3fy import Gns3Connector
from loguru import logger


def create_project(gns3: Gns3Connector, project_name: str, experiment_name: str, os_name: Optional[str]) -> dict:
    project_name = f'{project_name}-{experiment_name}' + (f'-{os_name}' if os_name is not None else '')
    project = gns3.create_project(name=project_name)
    logger.info(f'Project {project_name} created')
    return project


def find_and_delete_projects(gns3: Gns3Connector, project_name: str):
    projects = gns3.get_projects()

    for project in projects:
        if project['name'].startswith(project_name):
            logger.info(f'Deleting project {project['name']}')
            gns3.delete_project(project['project_id'])