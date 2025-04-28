import sys
from typing import Optional

import pexpect
from gns3fy import Node
from loguru import logger

from src.constants import EXPERIMENT_DURATION, EXPERIMENT_NAME, SERVER_IP, CLIENT_SIDE_NETWORK, SERVER_SIDE_NETWORK, ROUTER_SERVER_SIDE_IP, ROUTER_CLIENT_SIDE_IP


def connect(node: Node, rules: list[list[str]], log: bool):
    logger.info(f'Telnet start transmission')

    client = pexpect.spawn(f'telnet {node.console_host} {node.console}')

    client.logfile = None
    #client.logfile = sys.stdout.buffer
    client.sendline()

    for expect, send in rules:
        if log and client.logfile_read is None and expect == ':~':
            client.logfile_read = sys.stdout.buffer
        client.expect(expect, timeout=EXPERIMENT_DURATION*10)

        if send is None:
            break

        if send != '\n':
            print('\r', end='', flush=True)
            logger.info(f'> {send}')
        client.sendline(send)

    client.logfile = None
    client.sendline()
    print('\r', end='', flush=True)
    logger.info('Telnet end transmission')

def base_guest_rules(ip_address: str, router_ip: str, distant_network: str) -> list:
    return [
        ('ogin:', 'root'),
        ('assword:', 'debian'),
        (':~', 'ip link set ens4 up'),
        (':~', f'ip address add {ip_address}/24 dev ens4'),
        (':~', f'ip route add {distant_network}/24 via {router_ip} dev ens4'),
    ]

def client_test_rules(test_title: str) -> list:
    return [
        (':~', 'mkdir /mnt/shared'),
        (':~', 'mount -t 9p -o trans=virtio,version=9p2000.L shared_folder /mnt/shared'),
        (':~', f'flent {EXPERIMENT_NAME} -t {test_title} -l {EXPERIMENT_DURATION} -H {SERVER_IP}'),
        (':~', 'cp *.flent.gz /mnt/shared'),
    ]

def router_rules(input_ready: str, login: Optional[str], password: Optional[str], trigger_sequence: Optional[str], configuration: str|list, interface_prefix: str) -> list:
    rules = []

    if trigger_sequence is not None:
        rules += [(trigger_sequence, '\n')]

    if login is not None:
        rules += [('ogin:', login)]
    if password is not None:
        rules += [('assword:', password)]


    match configuration:
        case 'freebsd' | 'openbsd':
            rules += [
                (input_ready, f'ifconfig {interface_prefix}0 inet {ROUTER_CLIENT_SIDE_IP} netmask 255.255.255.0'),
                (input_ready, f'ifconfig {interface_prefix}1 inet {ROUTER_SERVER_SIDE_IP} netmask 255.255.255.0'),
                (input_ready, f'route add -net {CLIENT_SIDE_NETWORK}/24 -interface {interface_prefix}1'),
                (input_ready, f'route add -net {SERVER_SIDE_NETWORK}/24 -interface {interface_prefix}0'),
            ]
        case 'iproute2':
            rules += [
                (input_ready, 'sudo -i'),
                (input_ready, f'ip link set {interface_prefix}3 up'),
                (input_ready, f'ip link set {interface_prefix}4 up'),
                (input_ready, f'ip address add {ROUTER_CLIENT_SIDE_IP}/24 dev {interface_prefix}3'),
                (input_ready, f'ip address add {ROUTER_SERVER_SIDE_IP}/24 dev {interface_prefix}4'),
                (input_ready, 'echo 1 > /proc/sys/net/ipv4/ip_forward'),
            ]
        case 'none':
            rules += []
        case _:
            logger.warning('Unknown OS network stack configuration type, using the provided commands')
            for command in configuration:
                command = format_custom_command(command, interface_prefix)
                rules += [(input_ready, command)]

    return rules

def format_custom_command(command: str, interface_prefix: str) -> str:
    return (command
        .replace("{INTERFACE_PREFIX}", interface_prefix)
        .replace("{ROUTER_CLIENT_SIDE_IP}", ROUTER_CLIENT_SIDE_IP)
        .replace("{ROUTER_SERVER_SIDE_IP}", ROUTER_SERVER_SIDE_IP)
        .replace("{CLIENT_SIDE_NETWORK}", CLIENT_SIDE_NETWORK)
        .replace("{SERVER_SIDE_NETWORK}", SERVER_SIDE_NETWORK)
    ) + "\r"
