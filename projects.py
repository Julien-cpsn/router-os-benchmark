from gns3fy import Gns3Connector
from loguru import logger

from constants import PROJECT_NAME


def create_project(gns3: Gns3Connector, os_name: str, run_index: int) -> dict:
    project_name = f'{PROJECT_NAME}-{os_name}-run-{run_index}'
    project = gns3.create_project(name=project_name)
    logger.info(f'Project {project_name} created')
    return project


def find_and_delete_projects(gns3: Gns3Connector):
    projects = gns3.get_projects()

    for project in projects:
        if project['name'].startswith(PROJECT_NAME):
            logger.info(f'Deleting project {project['name']}')
            gns3.delete_project(project['project_id'])