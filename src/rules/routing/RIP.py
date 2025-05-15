from src.rules.utils import rules_from_stack
from src.types import OperatingSystem, Node

def router_rip_rules(self: OperatingSystem, router: Node):
    rules = []

    match self.routing_stack:
        case 'bird2':
            rules += [(self.input_ready, 'cat >> /usr/local/etc/bird.conf << EOF\nprotocol rip {\n    ipv4 {\n        import all;\n        export where source = RTS_DEVICE;\n    };\n\nEOF')]

    for network_to_add in router.routes['RIP']['add_networks']:
        rules += router_rip_add_network_rules(
            self=self,
            network_to_add=network_to_add,
        )

    for interface_to_enable in router.routes['RIP']['enable_interfaces']:
        rules += router_rip_enable_interface_rules(
            self=self,
            interface_to_enable=interface_to_enable,
        )

    match self.routing_stack:
        case 'bird2':
            rules += [(self.input_ready, 'cat >> /usr/local/etc/bird.conf << EOF\n}\nEOF')]

    return rules

def router_rip_enable_interface_rules(self: OperatingSystem, interface_to_enable: int) -> list:
    interface_to_enable = self.interfaces_start_at + interface_to_enable

    return rules_from_stack(
        self=self,
        stack=self.routing_stack,
        cases={
            'frr': ('#', [
                f'interface {self.interface_prefix}{interface_to_enable}',
                'ip rip send version 2',
                'ip rip receive version 2',
                'exit'
            ]),
            'quagga': (None, []),
            'bird2': (None, [f'''cat >> /usr/local/etc/bird.conf << EOF\n    interface "{self.interface_prefix}{interface_to_enable}" {{\n        version 2;\n        update time 30;\n    }};\nEOF''']),
            'holo': (None, []),
            'gobgp': (None, []),
        },
        custom_command_keys=['RIP', 'enable_interface'],
        custom_command_args={
            'interface': interface_to_enable
        }
    )

def router_rip_add_network_rules(self: OperatingSystem, network_to_add: str) -> list:
    return rules_from_stack(
        self=self,
        stack=self.routing_stack,
        cases={
            'frr': ('#', [
                'router rip',
                'version 2',
                f'network {network_to_add}',
                'redistribute connected',
                'exit'
            ]),
            'quagga': (None, []),
            'bird2': (None, []),
            'holo': (None, []),
            'gobgp': (None, []),
        },
        custom_command_keys=['RIP', 'add_network'],
        custom_command_args={
            'distant_network': network_to_add
        }
    )