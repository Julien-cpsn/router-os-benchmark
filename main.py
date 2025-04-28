import os

from gns3fy import Gns3Connector
from loguru import logger

from src.config import get_gns3_images_path
from src.constants import GNS3_SERVER_URL, GNS3_SERVER_USERNAME, GNS3_SERVER_PASSWORD, SERVER_IP, ROUTER_CLIENT_SIDE_IP, \
    ROUTER_SERVER_SIDE_IP, CLIENT_SIDE_NETWORK, SERVER_SIDE_NETWORK, CLIENT_IP, OS_LIST, NUMBER_OF_RUNS, ROUTER_NIC, \
    EXPERIMENT_DURATION, ROUTER_VCPU, ROUTER_RAM, GUEST_IMAGE_PATH
from src.images import find_or_upload_image
from src.links import link_nodes
from src.logger import def_context
from src.nodes import create_node
from src.projects import create_project, find_and_delete_projects
from src.telnet import connect, base_guest_rules, client_test_rules, router_rules
from src.templates import generate_template, generate_debian_template

with def_context(name="GNS3", part='Config'):
    images_path = get_gns3_images_path()
    try:
        gns3 = Gns3Connector(GNS3_SERVER_URL, user=GNS3_SERVER_USERNAME, cred=GNS3_SERVER_PASSWORD)
        gns3.get_version()
        find_and_delete_projects(gns3)
    except Exception as e:
        logger.error(e)
        exit(1)
    guest_image_name = os.path.basename(GUEST_IMAGE_PATH)
    find_or_upload_image(gns3, images_path=images_path, image_name=guest_image_name, image_path=GUEST_IMAGE_PATH)

try:
    for os_name in OS_LIST:
        os_input_ready = OS_LIST[os_name]['input_ready']
        os_login = OS_LIST[os_name]['login']
        os_password = OS_LIST[os_name]['password']
        trigger_sequence = OS_LIST[os_name]['trigger_sequence']
        os_configuration = OS_LIST[os_name]['configuration']
        interface_prefix = OS_LIST[os_name]['interface_prefix']
        os_image_path = OS_LIST[os_name]['image_path']
        os_image_name = os.path.basename(os_image_path)

        with def_context(name=os_name, node='Router', part='Template'):
            find_or_upload_image(gns3, images_path=images_path, image_name=os_image_name, image_path=os_image_path)
            generate_template(gns3, name=os_name, image_name=os_image_name)

        for run_index in range(1, NUMBER_OF_RUNS+1):
            test_title = f'"{os_name}__{EXPERIMENT_DURATION}s-{ROUTER_NIC}-cpu_{ROUTER_VCPU}-ram_{ROUTER_RAM}-run_{run_index}"'

            # GNS3 & Config
            with def_context(name=os_name, run=run_index, node='Project'):
                project = create_project(gns3, os_name=os_name, run_index=run_index)
                project_id = project['project_id']

            with def_context(name=os_name, run=run_index, node='Debian', part='Template'):
                generate_debian_template(gns3, image_name='debian-bookworm.qcow2', router_os_name=os_name)

            # Client
            with def_context(name=os_name, run=run_index, node='Client', part='Start'):
                client = create_node(gns3, project_id=project_id, name="Client", template="Debian guest", x=-200, y=-8)
                client.start()

            # Server
            with def_context(name=os_name, run=run_index, node='Server', part='Start'):
                server = create_node(gns3, project_id=project_id, name="Server", template="Debian guest", x=200, y=-8)
                server.start()

            with def_context(name=os_name, run=run_index, node='Router', part='Start'):
                router = create_node(gns3, project_id=project_id, name='Router', template=os_name, x=0)
                router.start()

            with def_context(name=os_name, run=run_index, node='All', part='Linking'):
                link_nodes(gns3, project_id, router, client, server)

            with def_context(name=os_name, run=run_index, node='Client', part='Config'):
                connect(client, base_guest_rules(ip_address=CLIENT_IP, router_ip=ROUTER_CLIENT_SIDE_IP, distant_network=SERVER_SIDE_NETWORK), log=False)
            with def_context(name=os_name, run=run_index, node='Server', part='Config'):
                connect(server, base_guest_rules(ip_address=SERVER_IP, router_ip=ROUTER_SERVER_SIDE_IP, distant_network=CLIENT_SIDE_NETWORK), log=False)

            with def_context(name=os_name, run=run_index, node='Router', part='Config'):
                connect(
                    router,
                    router_rules(
                        input_ready=os_input_ready,
                        login=os_login,
                        password=os_password,
                        trigger_sequence=trigger_sequence,
                        configuration=os_configuration,
                        interface_prefix=interface_prefix
                    ),
                    log=True
                )

            with def_context(name=os_name, run=run_index, node='Client', part='Experiment'):
                connect(client, client_test_rules(test_title=test_title), log=True)

            #exit(1)
            router.stop()
            client.stop()
            server.stop()
except KeyboardInterrupt as e:
    with def_context(name="GNS3", part='Exiting'):
        print('\r', end='', flush=True)
        logger.info("Exiting...")
        try:
            router.stop()
        except:
            print()

        try:
            client.stop()
        except:
            print()

        try:
            server.stop()
        except:
            print()