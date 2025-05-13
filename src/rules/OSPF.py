from typing import Optional

from src.rules.utils import preformat_custom_command

# Une seule zone OSPF

def router_add_ospf_route_rules(input_ready: str, configuration: Optional[str|dict], distant_network: str, gateway: str) -> list:
    if configuration is None:
        return []

    rules = []

    if isinstance(configuration, str):
        match configuration:
            case 'freebsd' | 'openbsd':
                rules += []
            case 'iproute2':
                rules += []
    else:
        add_ip_route_commands = configuration['add_ip_route']
        for command in add_ip_route_commands:
            rules += [
                (input_ready, preformat_custom_command(command=command, distant_network=distant_network, gateway=gateway)),
            ]

    return rules