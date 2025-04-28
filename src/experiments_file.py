import json
import jsonschema
from loguru import logger
schema = {
    'type': 'object',
    'properties': {
        'config': {
            'type': 'object',
            'properties': {
                'gns3_url': {'type': 'string'},
                'gns3_server_username': {'type': 'string'},
                'gns3_server_password': {'type': 'string'},
                'project_name': {'type': 'string'},
                'guest_image_path': {'type': 'string'},
            },
            'required': ['gns3_url', 'gns3_server_username', 'gns3_server_password', 'project_name', 'guest_image_path'],
        },
        'experiment': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'duration': {'type': 'integer'},
                'runs': {'type': 'integer'},
                'router_vcpu': {'type': 'integer'},
                'router_ram': {'type': 'integer'},
                'router_nic': {'type': 'string'},
                'guest_vcpu': {'type': 'integer'},
                'guest_ram': {'type': 'integer'},
                'client_side_network': {'type': 'string'},
                'server_side_network': {'type': 'string'},
            },
            'required': ['name', 'duration', 'runs', 'router_vcpu', 'router_ram', 'router_nic', 'guest_vcpu', 'guest_ram', 'client_side_network', 'server_side_network'],
        },
        'os_list': {
            'type': 'object',
            'additionalProperties': {
                'type': 'object',
                'properties': {
                    'input_ready': {'type': 'string'},
                    'trigger_sequence': {'type': ['string', 'null']},
                    'login': {'type': ['string', 'null']},
                    'password': {'type': ['string', 'null']},
                    'configuration': {'type': ['string', 'array']},
                    'interface_prefix': {'type': 'string'},
                    'image_path': {'type': 'string'}
                },
                'required': ['input_ready', 'login', 'password', 'trigger_sequence', 'configuration', 'interface_prefix', 'image_path']
            }
        },
    },
    'required': ['config', 'experiment', 'os_list'],
}


with open('experiments.json', 'r') as f:
    json_data = json.load(f)

    try:
        jsonschema.validate(instance=json_data, schema=schema)
    except Exception as e:
        logger.error(e)
        exit(1)

    experiments = json_data