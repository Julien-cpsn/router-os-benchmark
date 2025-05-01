from typing import Optional

from src.types import Node, OperatingSystem, Test
from src.utils import sanitize_string


class Constants:
    def __init__(self, experiment_data: dict):
        self.ROUTERS: list[Node] = []
        self.GUESTS: list[Node] = []
        self.TESTS: list[Test] = []
    
        self.EXPERIMENT_NAME = sanitize_string(experiment_data['experiment_name'])
        self.PLOT_LEGEND_WHEN_MERGED: Optional[str] = experiment_data['plot_legend_when_merged']
        self.PROJECT_NAME: str = experiment_data['config']['project_name']
        self.TEMPLATE_PREFIX: str = experiment_data['config']['template_prefix']
        self.GUEST_IMAGE_PATH: str = experiment_data['config']['guest_image_path']
        self.GNS3_SERVER_URL: str = experiment_data['config']['gns3']['url']
        self.GNS3_SERVER_USERNAME: str = experiment_data['config']['gns3']['server_username']
        self.GNS3_SERVER_PASSWORD: str = experiment_data['config']['gns3']['server_password']
        self.LINKS: list[dict] = experiment_data['network']['links']
    
        for test in experiment_data['tests']:
            test['from_node'] = test['from']
            test['to_node'] = test['to']
            del test['from']
            del test['to']
            self.TESTS.append(Test(**test))
        
        self.SHOULD_ITERATE_OVER_OS_LIST = False
        self.OS_LIST = self.json_to_os_list(experiment_data['os_list'])
        self.OS_TO_TEST = self.define_oses_to_test(nodes=experiment_data['network']['nodes'])

    def json_to_os_list(self, json_input: dict) -> dict[str, OperatingSystem]:
        operating_system_list = {}

        for name, operating_system in json_input.items():
            operating_system['name'] = name
            operating_system_list[name] = OperatingSystem(**operating_system)

        return operating_system_list

    def define_oses_to_test(self, nodes: dict) -> dict[str, OperatingSystem]:
        os_to_test = {}

        for name, node in nodes.items():
            if os_to_test != self.OS_LIST and node['type'] == 'router':
                os_name = node['os']

                if os_name is None:
                    os_to_test = self.OS_LIST
                    self.SHOULD_ITERATE_OVER_OS_LIST = True
                else:
                    found_os = None

                    for operating_system in self.OS_LIST.values():
                        if operating_system.name == os_name:
                            found_os = operating_system
                            break

                    if found_os is None:
                        print(f'OS {os_name} not found in os_list')
                        exit(1)

                    os_to_test[os_name] = found_os

            node['name'] = name
            node['node_type'] = node['type']
            del node['type']
            node = Node(**node)

            match node.node_type:
                case 'guest':
                    self.GUESTS.append(node)
                case 'router':
                    self.ROUTERS.append(node)

        return os_to_test