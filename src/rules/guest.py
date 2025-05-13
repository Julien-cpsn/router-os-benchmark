import os
from typing import Optional


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