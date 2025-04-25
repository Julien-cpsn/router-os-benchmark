import configparser
import os
import platform
import sys
from configparser import ConfigParser

from loguru import logger


def find_gns3_config() -> tuple[str, ConfigParser]:
    logger.info("Finding GNS3 Configuration file")
    config = None
    config_path = None

    if platform.system() == "Darwin":
        config_paths = [
            '~/.config/GNS3/gns3_server.conf'
        ]
    elif platform.system() == "Windows":
        config_paths = [
            "%APPDATA%/GNS3/gns3_server.ini"
            "%APPDATA%/Roaming/GNS3/gns3_server.ini"
            "%APPDATA%/GNS3.ini"
            "%COMMON_APPDATA%/GNS3/gns3_server.ini"
            "%COMMON_APPDATA%/GNS3.ini"
        ]
    else:
        config_paths = [
            '~/.config/GNS3/2.2/gns3_server.conf',
            '~/.config/GNS3.conf',
            '/etc/xdg/GNS3/gns3_server.conf',
            '/etc/xdg/GNS3.conf',
        ]

    for path in config_paths:
        path = os.path.expanduser(path)
        if os.path.exists(path):
            config = open(path).read()
            config_path = path
            logger.info(f"Found GNS3 Configuration file: {path}")
            break

    if config is None or config_path is None:
        logger.error("GNS3 Configuration file not found")
        sys.exit(1)

    config_parser = configparser.ConfigParser(allow_no_value=True)
    config_parser.read_string(config)
    logger.info("Config parsed")
    return config_path, config_parser

def get_gns3_images_path() -> str:
    logger.info("Getting GNS3 Images Path")
    config_path, config = find_gns3_config()

    try:
        qemu_unsafe_options = config['Qemu']['allow_unsafe_options']

        if qemu_unsafe_options not in ['True', 'False']:
            logger.error("[Qemu] allow_unsafe_options is not a bool")
            sys.exit(1)

        if qemu_unsafe_options == 'False':
            config.set('Qemu', 'allow_unsafe_options', 'True')
            config.write(open(config_path, 'w'))
            logger.info(f"Qemu allow_unsafe_options has been set to True")
        else:
            logger.info(f"Qemu allow_unsafe_options is set to True")

    except KeyError:
        logger.info(f"Adding Qemu allow_unsafe_options and setting it to True")
        config.add_section('Qemu')
        config.set('Qemu', '; Allow unsafe additional command line options')
        config.set('Qemu', 'allow_unsafe_options', 'True')
        logger.info(f"Writing new config to config file")
        config.write(open(config_path, 'w'))
    try:
        images_path = config['Server']['images_path']

        if not isinstance(images_path, str):
            logger.error("[Server] images_path is not a string")
            sys.exit(1)

        if not os.path.exists(images_path):
            logger.error("[Server] images_path path doest not exist")
            sys.exit(1)

        logger.info(f"Found GNS3 Images Path: {images_path}")
        return images_path
    except KeyError:
        logger.error("[Server] images_path not found in GNS3 Configuration file")
        sys.exit(1)