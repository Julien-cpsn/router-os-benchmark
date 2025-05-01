import os
import sys
from typing import Optional

import pexpect
from gns3fy import Node
from loguru import logger

from src.logger import def_context


def connect(context_name: str, section: str, part: str, node: Node, rules: list[list[str]], log: bool):
    with def_context(name=context_name, section=section, part=part):
        logger.info(f'Telnet start transmission')

        try:
            client = pexpect.spawn(f'telnet {node.console_host} {node.console}')

            client.logfile = None
            #client.logfile = sys.stdout.buffer
            client.sendline()

            for expect, send in rules:
                if log and client.logfile_read is None and expect == ':~':
                    client.logfile_read = sys.stdout.buffer
                client.expect(expect, timeout=600)

                if send is None:
                    break

                if send != '\n':
                    print('\r', end='', flush=True)
                    logger.info(f'> {send}')

                client.sendline(send)

            client.logfile = None
            client.sendline()
            client.close(force=True)
            print('\r', end='', flush=True)
            logger.info('Telnet end transmission')
        except Exception as e:
            logger.error(e)
            exit(1)

def guest_base_config(ip_address: str) -> list:
    return [
        ('ogin:', 'root'),
        ('assword:', 'debian'),
        (':~', 'ip link set ens4 up'),
        (':~', f'ip address add {ip_address}/24 dev ens4'),
    ]

def guest_add_route(distant_network: str, router_ip: str) -> list:
    return [
        (':~', f'ip route add {distant_network}/24 via {router_ip} dev ens4')
    ]

def client_test_rules(experiment_name: str, test: str, test_name: str, duration: int, server_ip: str, os_name: Optional[str]) -> list:
    local_path = f'shared/{experiment_name}/{test_name}'
    shared_path = f'/mnt/shared/{experiment_name}/{test_name}'

    if os_name is not None:
        local_path += f'/{os_name}'
        shared_path += f'/{os_name}'
        test_tile = os_name
    else:
        test_tile = experiment_name

    os.makedirs(local_path, exist_ok=True)

    return [
        (':~', 'mkdir /mnt/shared'),
        (':~', 'mount -t 9p -o trans=virtio,version=9p2000.L shared_folder /mnt/shared'),
        (':~', f'flent {test} -t {test_tile} -l {duration} -H {server_ip}'),
        (':~', f'cp *.flent.gz {shared_path}'),
        (':~', None),
    ]

def router_login_rules(input_ready: str, login: Optional[str], password: Optional[str], trigger_sequence: Optional[str], configuration: Optional[str|dict]) -> list:
    rules = []

    if trigger_sequence is not None:
        rules += [(trigger_sequence, '\n')]

    if login is not None:
        rules += [('ogin:', login)]
    if password is not None:
        rules += [('assword:', password)]

    if configuration is None:
        return rules

    if isinstance(configuration, str):
        match configuration:
            case 'freebsd' | 'openbsd':
                rules += []
            case 'iproute2':
                rules += [
                    (input_ready, 'sudo -i'),
                    (input_ready, 'echo 1 > /proc/sys/net/ipv4/ip_forward'),
                ]
    else:
        start = configuration['start']
        for command in start:
            rules += [
                (input_ready, preformat_custom_command(command=command)),
            ]


    return rules

def router_add_ip_address_rules(input_ready: str, configuration: Optional[str|dict], ip_address: str, interface_prefix: str, interfaces_start_at: int, interface: int) -> list:
    if configuration is None:
        return []

    rules = []

    if isinstance(configuration, str):
        match configuration:
            case 'freebsd' | 'openbsd':
                rules += [
                    (input_ready, f'ifconfig {interface_prefix}{interfaces_start_at + interface} inet {ip_address} netmask 255.255.255.0'),
                ]
            case 'iproute2':
                rules += [
                    (input_ready, f'ip link set dev {interface_prefix}{interfaces_start_at +interface} up'),
                    (input_ready, f'ip address add {ip_address}/24 dev {interface_prefix}{interfaces_start_at +interface}'),
                ]
    else:
        add_ip_address_commands = configuration['add_ip_address']
        for command in add_ip_address_commands:
            rules += [
                (input_ready, preformat_custom_command(command=command, ip_address=ip_address, interface_prefix=interface_prefix, interface=(interfaces_start_at + interface))),
            ]

    return rules

def router_add_ip_route_rules(input_ready: str, configuration: Optional[str|dict], distant_network: str, gateway: str, interface_prefix: str, interfaces_start_at: int, interface: int) -> list:
    if configuration is None:
        return []

    rules = []

    if isinstance(configuration, str):
        match configuration:
            case 'freebsd' | 'openbsd':
                rules += [
                    (input_ready, f'route add -net {distant_network}/24 -interface {interface_prefix}{interfaces_start_at + interface}'),
                ]
            case 'iproute2':
                rules += []
    else:
        add_ip_route_commands = configuration['add_ip_route']
        for command in add_ip_route_commands:
            rules += [
                (input_ready, preformat_custom_command(command=command, distant_network=distant_network, gateway=gateway, interface_prefix=interface_prefix, interface=(interfaces_start_at + interface))),
            ]

    return rules

def preformat_custom_command(command: str, ip_address: Optional[str] = None, distant_network: Optional[str] = None, gateway: Optional[str] = None, interface_prefix: Optional[str] = None, interface: Optional[int] = None) -> str:
    return (command
        .replace('{IP_ADDRESS}', ip_address if ip_address is not None else '')
        .replace('{DISTANT_NETWORK}', distant_network if distant_network is not None else '')
        .replace('{GATEWAY}', gateway if gateway is not None else '')
        .replace('{INTERFACE_PREFIX}', interface_prefix if interface_prefix is not None else '')
        .replace('{INTERFACE}', str(interface)  if interface is not None else '')
    ) + '\r'