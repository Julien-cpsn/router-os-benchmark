import os
from uuid import uuid4

from gns3fy import Gns3Connector
from loguru import logger

from constants import ROUTER_VCPU, ROUTER_RAM, GUEST_VCPU, GUEST_RAM, ROUTER_NIC


def generate_template(gns3: Gns3Connector, name: str, image_name: str):
  try:
    logger.info('Deleting template if exists')
    gns3.delete_template(name)
  except Exception as e:
    logger.warning(e)

  template = {
    "adapter_type": ROUTER_NIC,
    "adapters": 6,
    "bios_image": "",
    "boot_priority": "c",
    "builtin": False,
    "category": "router",
    "cdrom_image": "",
    "compute_id": "local",
    "console_auto_start": False,
    "console_type": "telnet",
    "cpu_throttling": 0,
    "cpus": ROUTER_VCPU,
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
    "name": name,
    "on_close": "power_off",
    "options": '',
    "platform": '',
    "port_name_format": 'Ethernet{0}',
    "port_segment_size": 0,
    "process_priority": "normal",
    "qemu_path": "qemu-system-x86_64",
    "ram": ROUTER_RAM,
    "replicate_network_connection_state": True,
    "symbol": ":/symbols/classic/router.svg",
    "template_id": str(uuid4()),
    "template_type": "qemu",
    "tpm": False,
    "uefi": False,
    "usage": ""
  }

  template = gns3.create_template(**template)
  logger.info('Generated template')

  return template

def generate_debian_template(gns3: Gns3Connector, image_name: str, router_os_name: str):
  try:
    logger.info('Deleting template if exists')
    gns3.delete_template("Debian guest")
  except Exception as e:
    logger.warning(e)

  shared_folder_path = f'{os.getcwd()}/shared/{router_os_name}'
  os.makedirs(shared_folder_path, exist_ok=True)

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
    "cpus": GUEST_VCPU,
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
    "name": "Debian guest",
    "on_close": "power_off",
    "options": f'-virtfs local,path="{shared_folder_path}",mount_tag=shared_folder,id=shared_folder,security_model=mapped-xattr',
    "platform": "",
    "port_name_format": "ens{port4}",
    "port_segment_size": 0,
    "process_priority": "normal",
    "qemu_path": "qemu-system-x86_64",
    "ram": GUEST_RAM,
    "replicate_network_connection_state": True,
    "symbol": "linux_guest.svg",
    "template_id": str(uuid4()),
    "template_type": "qemu",
    "tpm": False,
    "uefi": False,
    "usage": "Username:\troot\nPassword:\tdebian"
  }

  template = gns3.create_template(**template)
  logger.info('Generated Debian template')

  return template