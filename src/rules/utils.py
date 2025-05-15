import re
from ipaddress import IPv4Address
from typing import Optional

from src.types import OperatingSystem

def find_highest_ip_address(ips: list[dict]) -> str:
    ip_objects = [IPv4Address(re.sub('/\d+', '', ip['ip'])) for ip in ips]
    highest_ip = max(ip_objects)
    return str(highest_ip)

def rules_from_stack(self: OperatingSystem, stack: Optional[str|dict], cases: dict[str, tuple[Optional[str], list[str]]], custom_command_keys: list[str], custom_command_args) -> list:
    if stack is None:
        return []

    rules = []

    if isinstance(stack, str):
        input_ready, commands = cases[stack]

        if input_ready is None:
            input_ready = self.input_ready

        for command in commands:
            rules.append((input_ready, command))
    elif isinstance(stack, dict):
        custom_commands = stack
        for key in custom_command_keys:
            custom_commands = custom_commands[key]

        for command in custom_commands:
            rules += [
                (self.input_ready, preformat_custom_command(command=command, self=self, **custom_command_args)),
            ]

    return rules

def preformat_custom_command(
        command: str,
        self: OperatingSystem,
        ip_address: Optional[str] = None,
        distant_network: Optional[str] = None,
        gateway: Optional[str] = None,
        interface: Optional[int] = None,
        router_id: Optional[str] = None,
        instance_name: Optional[str] = None,
        area_name: Optional[str] = None,
    ) -> str:
    return (command
        .replace('{IP_ADDRESS}', ip_address if ip_address is not None else '')
        .replace('{DISTANT_NETWORK}', distant_network if distant_network is not None else '')
        .replace('{GATEWAY}', gateway if gateway is not None else '')
        .replace('{INTERFACE_PREFIX}', self.interface_prefix if self.interface_prefix is not None else '')
        .replace('{INTERFACE}', str(interface)  if interface is not None else '')
        .replace('{ROUTER_ID}', router_id  if router_id is not None else '')
        .replace('{INSTANCE_NAME}', instance_name  if instance_name is not None else '')
        .replace('{AREA_NAME}', area_name if area_name is not None else '')
    ) + '\r'