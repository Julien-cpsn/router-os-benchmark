import os
from typing import Optional

import gns3fy
from loguru import logger

from src.utils import sanitize_string


class Node:
    def __init__(
            self,
            name: str,
            node_type: str,
            vcpu: int,
            ram: int,
            ip: Optional[str] = None,
            os: Optional[str] = None,
            nic: Optional[str] = None,
            adapters: Optional[int] = None,
            ips: Optional[list[dict]] = None,
            routes: Optional[dict] = None
        ):
        self.name = name
        self.node_type = node_type
        self.vcpu = vcpu
        self.ram = ram
        self.node_type = node_type
        self.gns3_node: Optional[gns3fy.Node] = None
        self.distant_networks: list[DistantNetwork] = []

        match node_type:
            case 'guest':
                self.ip = ip
            case 'router':
                self.os = os
                self.nic = nic
                self.adapters = adapters
                self.ips = ips
                self.routes = routes

    def get_adapter(self, index: int) -> dict:
        for ip in self.ips:
            if ip['adapter'] == index:
                return ip
        logger.error(f'Adapter {index} not found in node {self.name}')
        exit(1)

    def get_ip(self, index: int) -> str:
        match self.node_type:
            case 'guest':
                return self.ip
            case 'router':
                return self.get_adapter(index)['ip']
        exit(1)

class OperatingSystem:
    def __init__(self, name: str, input_ready: str, trigger_sequence: str, login: Optional[str], password: Optional[str], network_stack: str|dict[str, list[str]], routing_stack: Optional[str|dict[str, dict]], interface_prefix: str, interfaces_start_at: int, image_path: str):
        self.name = name
        self.input_ready = input_ready
        self.trigger_sequence = trigger_sequence
        self.login = login
        self.password = password
        self.network_stack = network_stack
        self.routing_stack = routing_stack
        self.interface_prefix = interface_prefix
        self.interfaces_start_at = interfaces_start_at
        self.image_path = image_path
        self.image_name = os.path.basename(image_path)

class Test:
    def __init__(self, name: str, test: str, fire_at: int, duration: int, from_node: str, to_node: str):
        self.name = sanitize_string(name)
        self.test = test
        self.fire_at = fire_at
        self.duration = duration
        self.from_node = from_node
        self.to_node = to_node

class DistantNetwork:
    def __init__(self, network: str, gateway: str, adapter: int):
        self.network = network
        self.gateway = gateway
        self.adapter = adapter