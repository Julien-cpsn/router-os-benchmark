from src.types import OperatingSystem
from src.rules.utils import rules_from_stack


def router_network_start_rules(self: OperatingSystem) -> list:
    return rules_from_stack(
        self=self,
        stack=self.network_stack,
        cases={
            **dict.fromkeys(['openbsd', 'freebsd'], (None, [])),
            'iproute2': (None, [
                'sudo -i', # May not work on some OS, but it doesn't matter
                'echo 1 > /proc/sys/net/ipv4/ip_forward',
            ])
        },
        custom_command_keys=['start'],
        custom_command_args={}
    )

def router_network_stack_stop_rules(self: OperatingSystem) -> list:
    return rules_from_stack(
        self=self,
        stack=self.network_stack,
        cases={
            **dict.fromkeys(['openbsd', 'freebsd'], (None, [])),
            'iproute2': (None, [
                'exit'
            ])
        },
        custom_command_keys=['stop'],
        custom_command_args={}
    )