from src.types import OperatingSystem
from src.rules.utils import rules_from_stack


def router_routing_stack_start_rules(self: OperatingSystem, router_id: str) -> list:
    return rules_from_stack(
        self=self,
        stack=self.routing_stack,
        cases={
            'frr': ('#', [
                'sysrc frr_enable=yes' if self.network_stack in ['freebsd', 'openbsd'] else None,
                'service frr start' if self.network_stack in ['freebsd', 'openbsd'] else None,
                'sudo vtysh',
                'configure terminal',
            ]),
            'quagga': (None, []),
            'bird2': (None, [
                'sysrc bird_enable=yes' if self.network_stack in ['freebsd', 'openbsd'] else None,
                'service bird start' if self.network_stack in ['freebsd', 'openbsd'] else None,
                f'cat > /usr/local/etc/bird.conf << EOF\nrouter id {router_id};\n\nprotocol device {{\n    scan time 10;\n}}\n\nprotocol kernel {{\n    ipv4 {{\n        export all;\n    }};\n}}\n\nprotocol direct {{\n    ipv4 {{\n        import all;\n    }};\n}}\nEOF'
            ]),
            'holo': (None, []),
            'gobgp': (None, []),
        },
        custom_command_keys=['start'],
        custom_command_args={}
    )

def router_routing_stack_stop_rules(self: OperatingSystem) -> list:
    return rules_from_stack(
        self=self,
        stack=self.routing_stack,
        cases={
            'frr': ('#', [
                'exit',
                'write memory',
                'end',
                'exit'
            ]),
            'quagga': (None, []),
            'bird2': (None, ['birdc configure']),
            'holo': (None, []),
            'gobgp': (None, []),
        },
        custom_command_keys=['stop'],
        custom_command_args={}
    )