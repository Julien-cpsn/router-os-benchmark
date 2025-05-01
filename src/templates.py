import os
from uuid import uuid4

from gns3fy import Gns3Connector
from loguru import logger


def find_and_delete_templates(gns3: Gns3Connector, template_prefix: str):
  templates = gns3.get_templates()

  for template in templates:
    if template['name'].startswith(template_prefix):
      logger.info(f'Deleting template {template['name']}')

      try:
        gns3.delete_template(name=template['name'])
      except Exception as e:
        if e.args[0] != "'NoneType' object is not subscriptable":
          logger.error(e)
          exit(1)

def generate_router_template(gns3: Gns3Connector, template_prefix: str, node_name: str, os_name: str, image_name: str, vcpu: int, ram: int, nic: str, adapters: int):
  template_name = f'{template_prefix} {os_name} {node_name}'

  template = {
    "adapter_type": nic,
    "adapters": adapters,
    "bios_image": "",
    "boot_priority": "c",
    "builtin": False,
    "category": "router",
    "cdrom_image": "",
    "compute_id": "local",
    "console_auto_start": False,
    "console_type": "telnet",
    "cpu_throttling": 0,
    "cpus": vcpu,
    "create_config_disk": False,
    "custom_adapters": [],
    "default_name_format": "{name}-{0}",
    "first_port_name": "",
    "hda_disk_image": image_name,
    "hda_disk_interface": "ide",
    "hdb_disk_image": "",
    "hdb_disk_interface": "none",
    "hdc_disk_image": "",
    "hdc_disk_interface": "none",
    "hdd_disk_image": "",
    "hdd_disk_interface": "none",
    "initrd": "",
    "kernel_command_line": "",
    "kernel_image": "",
    "legacy_networking": False,
    "linked_clone": True,
    "mac_address": "",
    "name": template_name,
    "on_close": "power_off",
    "options": '',
    "platform": '',
    "port_name_format": 'Ethernet{0}',
    "port_segment_size": 0,
    "process_priority": "normal",
    "qemu_path": "qemu-system-x86_64",
    "ram": ram,
    "replicate_network_connection_state": True,
    "symbol": ":/symbols/classic/router.svg",
    "template_id": str(uuid4()),
    "template_type": "qemu",
    "tpm": False,
    "uefi": False,
    "usage": ""
  }

  template = gns3.create_template(**template)
  logger.info(f'Generated {template_name} template')

  return template

def generate_guest_template(gns3: Gns3Connector, template_prefix: str, name: str, image_name: str, vcpu: int, ram: int):
  template_name = f'{template_prefix} {name}'

  shared_folder_path = f'{os.getcwd()}/shared/'

  template = {
    "adapter_type": "virtio-net-pci",
    "adapters": 1,
    "bios_image": "",
    "boot_priority": "c",
    "builtin": False,
    "category": "guest",
    "cdrom_image": "",
    "compute_id": "local",
    "console_auto_start": False,
    "console_type": "telnet",
    "cpu_throttling": 0,
    "cpus": vcpu,
    "create_config_disk": False,
    "custom_adapters": [],
    "default_name_format": "{name}-{0}",
    "first_port_name": "",
    "hda_disk_image": image_name,
    "hda_disk_interface": "scsi",
    "hdb_disk_image": "",
    "hdb_disk_interface": "none",
    "hdc_disk_image": "",
    "hdc_disk_interface": "none",
    "hdd_disk_image": "",
    "hdd_disk_interface": "none",
    "initrd": "",
    "kernel_command_line": "",
    "kernel_image": "",
    "legacy_networking": False,
    "linked_clone": True,
    "mac_address": "",
    "name": template_name,
    "on_close": "power_off",
    "options": f'-virtfs local,path="{shared_folder_path}",mount_tag=shared_folder,id=shared_folder,security_model=mapped-xattr',
    "platform": "",
    "port_name_format": "ens{port4}",
    "port_segment_size": 0,
    "process_priority": "normal",
    "qemu_path": "qemu-system-x86_64",
    "ram": ram,
    "replicate_network_connection_state": True,
    "symbol": "linux_guest.svg",
    "template_id": str(uuid4()),
    "template_type": "qemu",
    "tpm": False,
    "uefi": False,
    "usage": "Username:\troot\nPassword:\tdebian"
  }

  template = gns3.create_template(**template)
  logger.info(f'Generated {template_name} template')

  return template