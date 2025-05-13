from typing_extensions import Optional

from src.rules.utils import preformat_custom_command


def router_login_rules(input_ready: str, login: Optional[str], password: Optional[str], trigger_sequence: Optional[str], network_stack: Optional[str|dict], routing_stack: Optional[str|dict]) -> list:
    rules = []

    if trigger_sequence is not None:
        rules += [(trigger_sequence, '\n')]

    if login is not None:
        rules += [('ogin:', login)]
    if password is not None:
        rules += [('assword:', password)]

    if network_stack is None:
        return rules

    if isinstance(network_stack, str):
        match network_stack:
            case 'freebsd' | 'openbsd':
                rules += []
            case 'iproute2':
                rules += [
                    (input_ready, 'sudo -i'),
                    (input_ready, 'echo 1 > /proc/sys/net/ipv4/ip_forward'),
                ]
    else:
        start = network_stack['start'] + routing_stack['start']
        for command in start:
            rules += [
                (input_ready, preformat_custom_command(command=command)),
            ]

    return rules

def router_stop_rules(input_ready: str, network_stack: Optional[str|dict], routing_stack: Optional[str|dict]) -> list:
    rules = []

    if network_stack is None:
        return rules

    if isinstance(network_stack, str):
        match network_stack:
            case 'freebsd' | 'openbsd':
                rules += []
            case 'iproute2':
                rules += []
    else:
        start = network_stack['stop'] + routing_stack['stop']
        for command in start:
            rules += [
                (input_ready, preformat_custom_command(command=command)),
            ]

    return rules