from src.rules.utils import rules_from_stack
from src.types import OperatingSystem

def router_add_ip_address_rules(self: OperatingSystem, ip_address: str, interface: int) -> list:
    interface = self.interfaces_start_at + interface

    return rules_from_stack(
        self=self,
        stack=self.network_stack,
        cases={
            **dict.fromkeys(['openbsd', 'freebsd'], (None, [
                f'ifconfig {self.interface_prefix}{interface} inet {ip_address} netmask 255.255.255.0',
            ])),
            'iproute2': (None, [
                f'ip link set dev {self.interface_prefix}{interface} up',
                f'ip address add {ip_address} dev {self.interface_prefix}{interface}'
            ])
        },
        custom_command_keys=['add_ip_address'],
        custom_command_args={
            'ip_address': ip_address,
            'interface': interface
        }
    )

def router_add_ip_route_rules(self: OperatingSystem, distant_network: str, gateway: str) -> list:
    return rules_from_stack(
        self=self,
        stack=self.network_stack,
        cases={
            **dict.fromkeys(['openbsd', 'freebsd'], (None, [
                f'route add -net {distant_network} {gateway}'
            ])),
            'iproute2': (None, [
                f'ip route add {distant_network} via {gateway}'
            ])
        },
        custom_command_keys=['add_static_route'],
        custom_command_args={
            'distant_network': distant_network,
            'gateway': gateway
        }
    )