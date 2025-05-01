import os

from gns3fy import Gns3Connector
from loguru import logger

from src.logger import def_context
from src.types import OperatingSystem


def find_or_upload_image(gns3: Gns3Connector, images_path: str, image_name: str, image_path: str):
    if os.path.exists(f'{images_path}/QEMU/{image_name}'):
        logger.info(f'Found image {image_name}')
    else:
        logger.info(f'Image {image_name} not found in GNS3')
        logger.info('Uploading image...')
        gns3.upload_compute_image(emulator='qemu', file_path=image_path)
        logger.info('Image uploaded to GNS3')

def ensure_images_are_uploaded(gns3: Gns3Connector, images_path: str, os_list: dict[str, OperatingSystem]):
    for operating_system in os_list.values():
        with def_context(name=operating_system.name, section='Image', part='Upload'):
            os_image_path = operating_system.image_path
            os_image_name = os.path.basename(os_image_path)
            find_or_upload_image(gns3, images_path=images_path, image_name=os_image_name, image_path=os_image_path)