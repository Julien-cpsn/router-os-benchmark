#!/usr/bin/env python3
import argparse
import json
import os


def FreeBSD_interface_prefix(nic: str) -> str:
    match nic:
        case 'E1000':
            return 'em'
        case 'RTL8139':
            return 're'
        case 'VirtIO':
            return 'vtnet'
        case _:
            raise ValueError(f'Unknown nic {nic}')

operating_systems = {
    'BSDRP': {
        "input_ready": ":~",
        "trigger_sequence": None,
        "login": "root",
        "password": None,
        "configuration": "freebsd",
        "interface_prefix": FreeBSD_interface_prefix,
        "interfaces_start_at": 0,
        "image_path": "/home/julien/Programmation/vm/BSDRP/BSDRP-1.993-full-amd64-serial.img"
    },
    'Debian': {
        "input_ready": ":~",
        "trigger_sequence": None,
        "login": "root",
        "password": "debian",
        "configuration": "iproute2",
        "interface_prefix": "ens",
        "interfaces_start_at": 3,
        "image_path": "/home/julien/Programmation/vm/Debian/tmp/debian-bookworm.qcow2"
    },
    'MikroTik': {
        "input_ready": " >",
        "trigger_sequence": None,
        "login": "admin",
        "password": "test",
        "configuration": {
            "start": [],
            "add_ip_address": ["ip address add address={IP_ADDRESS} interface={INTERFACE_PREFIX}{INTERFACE}"],
            "add_ip_route": ["ip route add dst-address={DISTANT_NETWORK}/24 gateway={INTERFACE_PREFIX}{INTERFACE}"]
        },
        "interface_prefix": "ether",
        "interfaces_start_at": 1,
        "image_path": "/home/julien/Programmation/vm/MikroTik/chr-6.49.18.img"
    },
    'SONiC': {
        "input_ready": ":~",
        "trigger_sequence": None,
        "login": "admin",
        "password": "YourPaSsWoRd",
        "configuration": "iproute2",
        "interface_prefix": "eth",
        "interfaces_start_at": 0,
        "image_path": "/home/julien/Programmation/vm/SONiC/sonic-vs-202411.img"
    },
    'VyOS': {
        "input_ready": ":~",
        "trigger_sequence": None,
        "login": "vyos",
        "password": "vyos",
        "configuration": "iproute2",
        "interface_prefix": "eth",
        "interfaces_start_at": 0,
        "image_path": "/home/julien/Programmation/vm/VyOS/vyos-2025.04.04-0018-rolling-generic-amd64.iso"
    }
}

resources = {
    'LR': {
        'vcpu': 1,
        'ram': 1024,
    },
    'MR': {
        'vcpu': 2,
        'ram': 2048,
    },
    'HR': {
        'vcpu': 4,
        'ram': 8096,
    }
}

nics = {
    'E1000': 'e1000',
    'RTL8139': 'rtl8139',
    'VirtIO': 'virtio-net-pci'
}

protocols = {
    'RIP': {},
    'OSPF': {},
    'BGP': {},
    'MPLS': {}
}

def main(generate_templates: bool):
    for os_name, os_config in operating_systems.items():
        for resources_name, resources_config in resources.items():
            for nic_name, nic in nics.items():
                for protocol_name, protocol_config in protocols.items():
                    directory = f'experiments/{os_name}/{resources_name}/{nic_name}'
                    file_name = f'simple-topology-{os_name}-{resources_name}-{nic_name}-{protocol_name}.json'
                    file_path = os.path.join(directory, file_name)

                    if generate_templates:
                        template = generate_template(os_name, os_config, resources_name, resources_config, nic_name, nic, protocol_name, protocol_config)
                        template_json = json.dumps(template, indent=2)

                        os.makedirs(directory, exist_ok=True)
                        file = open(file_path, 'w+')
                        file.write(template_json)

                        print(f"Wrote template to: {file_path}")
                    else:
                        print(f'-i {file_path} ', end='')

def generate_template(os_name: str, os_config: dict, resources_name: str, resources_config: dict, nic_name: str, nic: str, protocol_name: str, protocol_config: dict) -> dict:
    os_config_copy = os_config.copy()

    if callable(os_config['interface_prefix']):
        os_config_copy['interface_prefix'] = os_config['interface_prefix'](nic=nic_name)

    return {
      "experiment_name": f'Simple topology {os_name} {resources_name} {nic_name} {protocol_name}',
      "plot_legend_when_merged": f'{os_name} {resources_name} {nic_name} {protocol_name}',
      "config": {
        "project_name": "router-os-benchmark",
        "template_prefix": "Benchmark",
        "guest_image_path": "/home/julien/Programmation/vm/Debian/tmp/debian-bookworm.qcow2",
        "gns3": {
          "url": "http://127.0.0.1:3080",
          "server_username": "admin",
          "server_password": "gns3"
        }
      },
      "network": {
        "nodes": {
          "Client 1": {
            "type": "guest",
            "vcpu": 1,
            "ram": 1024,
            "ip": "10.0.1.2"
          },
          "Server 1": {
            "type": "guest",
            "vcpu": 1,
            "ram": 1024,
            "ip": "10.0.2.2"
          },
          "Router 1": {
            "type": "router",
            **resources_config,
            "os": os_name,
            "nic": nic,
            "adapters": 6,
            "ips": [
              { "adapter": 3, "ip": "10.0.1.1" },
              { "adapter": 4, "ip": "10.0.2.1" }
            ]
          }
        },
        "links": [
          { "node_a": "Client 1", "adapter_a": 0, "node_b": "Router 1", "adapter_b": 3 },
          { "node_a": "Server 1", "adapter_a": 0, "node_b": "Router 1", "adapter_b": 4 }
        ]
      },
      "tests": [
        {
          "name": "test1",
          "test": "rrul",
          "fire_at": 0,
          "duration": 60,
          "from": "Client 1",
          "to": "Server 1"
        }
      ],
      "os_list": {
        os_name: os_config_copy
      }
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='router-os-benchmark',
        description='Generate all possible cases within what is specified',
    )

    parser.add_argument('-o', '--os', dest='os')
    parser.add_argument('-r', '--resources', dest='resources', choices=resources.keys())
    parser.add_argument('-n', '--nic', dest='nic', choices=nics.keys())
    parser.add_argument('-p', '--protocol', dest='protocol', choices=protocols.keys())

    parser.add_argument('--generate-templates', dest='generate_templates', action='store_true', help="Generate experiment templates")
    args = parser.parse_args()

    if args.os is not None:
        operating_systems = {
            args.os: operating_systems[args.os]
        }

    if args.resources is not None:
        resources = {
            args.resources: resources[args.resources]
        }

    if args.nic is not None:
        nics = {
            args.nic: nics[args.nic]
        }

    if args.protocol is not None:
        protocols = {
            args.protocol: protocols[args.protocol]
        }

    main(args.generate_templates)