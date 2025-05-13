from typing import Optional

from src.rules.utils import preformat_custom_command


def router_add_ip_address_rules(input_ready: str, network_stack: Optional[str|dict], ip_address: str, interface_prefix: str, interfaces_start_at: int, interface: int) -> list:
    if network_stack is None:
        return []

    rules = []

    if isinstance(network_stack, str):
        match network_stack:
            case 'freebsd' | 'openbsd':
                rules += [
                    (input_ready, f'ifconfig {interface_prefix}{interfaces_start_at + interface} inet {ip_address} netmask 255.255.255.0'),
                ]
            case 'iproute2':
                rules += [
                    (input_ready, f'ip link set dev {interface_prefix}{interfaces_start_at + interface} up'),
                    (input_ready, f'ip address add {ip_address}/24 dev {interface_prefix}{interfaces_start_at + interface}'),
                ]
    else:
        add_ip_address_commands = network_stack['add_ip_address']
        for command in add_ip_address_commands:
            rules += [
                (input_ready, preformat_custom_command(command=command, ip_address=ip_address, interface_prefix=interface_prefix, interface=(interfaces_start_at + interface))),
            ]

    return rules

def router_add_ip_route_rules(input_ready: str, configuration: Optional[str|dict], distant_network: str, gateway: str) -> list:
    if configuration is None:
        return []

    rules = []

    if isinstance(configuration, str):
        match configuration:
            case 'freebsd' | 'openbsd':
                rules += [
                    (input_ready, f'route add -net {distant_network}/24 {gateway}'),
                ]
            case 'iproute2':
                rules += [
                    (input_ready, f'ip route add {distant_network}/24 via {gateway}'),
                ]
    else:
        add_ip_route_commands = configuration['add_ip_route']
        for command in add_ip_route_commands:
            rules += [
                (input_ready, preformat_custom_command(command=command, distant_network=distant_network, gateway=gateway)),
            ]

    return rules