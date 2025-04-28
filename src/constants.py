from src.experiments_file import experiments

GNS3_SERVER_URL = experiments['config']['gns3_url']
GNS3_SERVER_USERNAME = experiments['config']['gns3_server_username']
GNS3_SERVER_PASSWORD = experiments['config']['gns3_server_password']
PROJECT_NAME = experiments['config']['project_name']
GUEST_IMAGE_PATH = experiments['config']['guest_image_path']

EXPERIMENT_NAME = experiments['experiment']['name']
EXPERIMENT_DURATION = experiments['experiment']['duration']
NUMBER_OF_RUNS = experiments['experiment']['runs']
ROUTER_VCPU = experiments['experiment']['router_vcpu']
ROUTER_RAM = experiments['experiment']['router_ram']
ROUTER_NIC = experiments['experiment']['router_nic']
GUEST_VCPU = experiments['experiment']['guest_vcpu']
GUEST_RAM = experiments['experiment']['guest_ram']
CLIENT_SIDE_NETWORK = experiments['experiment']['client_side_network']
SERVER_SIDE_NETWORK = experiments['experiment']['server_side_network']

CLIENT_IP = CLIENT_SIDE_NETWORK[:-1] + '2'
SERVER_IP = SERVER_SIDE_NETWORK[:-1] + '2'
ROUTER_CLIENT_SIDE_IP = CLIENT_SIDE_NETWORK[:-1] + '1'
ROUTER_SERVER_SIDE_IP = SERVER_SIDE_NETWORK[:-1] + '1'

OS_LIST = experiments['os_list']