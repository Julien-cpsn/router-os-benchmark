import os
from threading import Timer
from typing import Optional

from gns3fy import Gns3Connector
from loguru import logger

from src.config import get_gns3_images_path
from src.constants import Constants
from src.images import find_or_upload_image, ensure_images_are_uploaded
from src.links import link_nodes, generate_routes_from_test, find_node
from src.logger import def_context
from src.nodes import create_node
from src.projects import create_project, find_and_delete_projects
from src.telnet import connect, guest_base_config, client_test_rules, router_login_rules, router_add_ip_address_rules, \
    guest_add_route, router_add_ip_route_rules
from src.templates import generate_router_template, generate_guest_template, find_and_delete_templates
from src.types import OperatingSystem


def main(constants: Constants):
    with def_context(name='Global'):
        logger.info(f'Running experiment {constants.EXPERIMENT_NAME}')

    # ----- GNS3/CONFIG -----

    with def_context(name='GNS3', part='Config'):
        images_path = get_gns3_images_path()
        try:
            gns3 = Gns3Connector(constants.GNS3_SERVER_URL, user=constants.GNS3_SERVER_USERNAME, cred=constants.GNS3_SERVER_PASSWORD)
            gns3.get_version()
            find_and_delete_projects(gns3, project_name=constants.PROJECT_NAME)
            find_and_delete_templates(gns3, template_prefix=constants.TEMPLATE_PREFIX)
        except Exception as e:
            logger.error(e)
            exit(1)

    # ----- GUEST -----

    with def_context(name='Guests', section='Image', part='Upload'):
        guest_image_name = os.path.basename(constants.GUEST_IMAGE_PATH)
        find_or_upload_image(gns3, images_path=images_path, image_name=guest_image_name, image_path=constants.GUEST_IMAGE_PATH)

    for guest in constants.GUESTS:
        with def_context(name=guest.name, section='Template', part='Generate'):
            generate_guest_template(
                gns3,
                template_prefix=constants.TEMPLATE_PREFIX,
                name=guest.name,
                image_name=guest_image_name,
                vcpu=guest.vcpu,
                ram=guest.ram
            )

    # ----- IMAGES -----

    ensure_images_are_uploaded(gns3, images_path, constants.OS_TO_TEST)

    # ----- TESTS -----

    if constants.SHOULD_ITERATE_OVER_OS_LIST:
        with def_context(name='Global'):
            logger.warning('Got a router node with "os = null", meaning that all provided OSes will be tested on that node')

        for operating_system in constants.OS_TO_TEST.values():
            with def_context(name=operating_system.name):
                logger.info(f'-------------------- {operating_system.name} --------------------')

            run_test(gns3, constants=constants, context_name=operating_system.name, rotation_os=operating_system)
    else:
        run_test(gns3, constants=constants, context_name=constants.EXPERIMENT_NAME, rotation_os=None)

def run_test(gns3: Gns3Connector, constants: Constants, context_name: str, rotation_os: Optional[OperatingSystem]):
    nodes = []

    try:
        with def_context(name=context_name, section='Project', part='Generate'):
            project = create_project(
                gns3,
                project_name=constants.PROJECT_NAME,
                experiment_name=constants.EXPERIMENT_NAME,
                os_name=None if rotation_os is None else rotation_os.name
            )
            project_id = project['project_id']

        for i, router in enumerate(constants.ROUTERS):
            # Using either the specified OS or the rotation one if none was provided
            operating_system = constants.OS_TO_TEST[router.os] if router.os is not None else rotation_os

            with def_context(name=context_name, section=router.name, part='Template'):
                generate_router_template(
                    gns3,
                    template_prefix=constants.TEMPLATE_PREFIX,
                    node_name=router.name,
                    os_name=operating_system.name,
                    image_name=operating_system.image_name,
                    vcpu=router.vcpu,
                    ram=router.ram,
                    nic=router.nic,
                    adapters=router.adapters
                )
            with def_context(name=context_name, section=router.name, part='Node'):
                gns3_node = create_node(
                    gns3,
                    template_prefix=constants.TEMPLATE_PREFIX,
                    project_id=project_id,
                    node_name=router.name,
                    os_name=operating_system.name,
                    x=200 * i,
                    y=0
                )
                router.gns3_node = gns3_node
                nodes.append(router)

        for i, guest in enumerate(constants.GUESTS):
            with def_context(name=context_name, section=guest.name, part='Node'):
                gns3_node = create_node(
                    gns3,
                    template_prefix=constants.TEMPLATE_PREFIX,
                    project_id=project_id,
                    node_name=guest.name,
                    os_name=None,
                    x=200 * i,
                    y=200
                )
                guest.gns3_node = gns3_node
                nodes.append(guest)

        with def_context(name=context_name, section='Nodes', part='Linking'):
            for link in constants.LINKS:
                link_nodes(gns3, project_id=project_id, nodes=nodes, link=link)

        with def_context(name=context_name, section='Test', part='Routes'):
            generate_routes_from_test(constants.TESTS, nodes)

        for node in nodes:
            with def_context(name=context_name, section=node.name, part='Start'):
                logger.info(f'Starting {node.name}')
                node.gns3_node.start()

        # ----- CONFIG -----

        for guest in constants.GUESTS:
            rules = guest_base_config(ip_address=guest.ip)

            for distant_network in guest.distant_networks:
                rules += guest_add_route(
                    distant_network=distant_network.network,
                    router_ip=distant_network.gateway
                )

            connect(
                context_name,
                guest.name,
                'Config',
                guest.gns3_node,
                rules,
                False
            )

        for router in constants.ROUTERS:
            # Using either the specified OS or the rotation one if none was provided
            operating_system = constants.OS_TO_TEST[router.os] if router.os is not None else rotation_os

            rules = []

            rules += router_login_rules(
                input_ready=operating_system.input_ready,
                login=operating_system.login,
                password=operating_system.password,
                trigger_sequence=operating_system.trigger_sequence,
                configuration=operating_system.configuration,
            )

            for ip in router.ips:
                rules += router_add_ip_address_rules(
                    input_ready=operating_system.input_ready,
                    configuration=operating_system.configuration,
                    ip_address=ip['ip'],
                    interface_prefix=operating_system.interface_prefix,
                    interfaces_start_at=operating_system.interfaces_start_at,
                    interface=ip['adapter'],
                )

            for distant_network in router.distant_networks:
                rules += router_add_ip_route_rules(
                    input_ready=operating_system.input_ready,
                    configuration=operating_system.configuration,
                    distant_network=distant_network.network,
                    gateway=distant_network.gateway,
                    interface_prefix=operating_system.interface_prefix,
                    interfaces_start_at=operating_system.interfaces_start_at,
                    interface=distant_network.adapter
                )

            connect(
                context_name,
                router.name,
                'Config',
                router.gns3_node,
                rules,
                True
            )

        # ----- TESTS -----

        test_threads: list[Timer] = []

        for test in constants.TESTS:
            with def_context(name=context_name, section='Test', part=test.name):
                from_node = find_node(nodes, test.from_node)
                to_node = find_node(nodes, test.to_node)

            rules = client_test_rules(
                experiment_name=constants.EXPERIMENT_NAME,
                test=test.test,
                test_name=test.name,
                duration=test.duration,
                server_ip=to_node.ip,
                os_name=rotation_os.name if rotation_os is not None else None,
            )

            test_thread = Timer(
                test.fire_at,
                connect,
                (
                    context_name,
                    'Test',
                    test.name,
                    from_node.gns3_node,
                    rules,
                    True
                )
            )
            test_threads.append(test_thread)

        for test_thread in test_threads:
            test_thread.start()
            test_thread.join()

        test_threads.clear()

        with def_context(name='GNS3', section='Nodes', part='Stop'):
            for node in nodes:
                logger.info(f'Shutting down node {node.name}')
                node.gns3_node.stop()
        # exit(1)

    except KeyboardInterrupt as e:
        with def_context(name='GNS3', part='Exiting'):
            print('\r', end='', flush=True)
            logger.info('Shutting down nodes...')

            try:
                for node in nodes:
                    node.gns3_node.stop()
            except:
                print()
        exit(1)