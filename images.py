import os

from gns3fy import Gns3Connector
from loguru import logger


def find_or_upload_image(gns3: Gns3Connector, images_path: str, image_name: str, image_path: str):
    if os.path.exists(f'{images_path}/QEMU/{image_name}'):
        logger.info(f'Found image {image_name}')
    else:
        logger.info(f'Image {image_name} not found in GNS3')
        logger.info('Uploading image...')
        gns3.upload_compute_image(emulator='qemu', file_path=image_path)
        logger.info('Image uploaded to GNS3')