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
    'BSDRP_FRR': {
        "input_ready": ":~",
        "trigger_sequence": None,
        "login": "root",
        "password": None,
        "network_stack": "freebsd",
        "routing_stack": "frr",
        "interface_prefix": FreeBSD_interface_prefix,
        "interfaces_start_at": 0,
        "image_path": "/home/julien/Programmation/vm/BSDRP/BSDRP-1.993-full-amd64-serial.img"
    },
    'BSDRP_BIRD2': {
        "input_ready": ":~",
        "trigger_sequence": None,
        "login": "root",
        "password": None,
        "network_stack": "freebsd",
        "routing_stack": "bird2",
        "interface_prefix": FreeBSD_interface_prefix,
        "interfaces_start_at": 0,
        "image_path": "/home/julien/Programmation/vm/BSDRP/BSDRP-1.993-full-amd64-serial.img"
    },
    'Debian': {
        "input_ready": ":~",
        "trigger_sequence": None,
        "login": "root",
        "password": "debian",
        "network_stack": "iproute2",
        "routing_stack": None,
        "interface_prefix": "ens",
        "interfaces_start_at": 3,
        "image_path": "/home/julien/Programmation/vm/Debian/tmp/debian-bookworm.qcow2"
    },
    'MikroTik': {
        "input_ready": " >",
        "trigger_sequence": None,
        "login": "admin",
        "password": "test",
        "network_stack": {
            "start": [],
            "add_ip_address": ["ip address add address={IP_ADDRESS} interface={INTERFACE_PREFIX}{INTERFACE}"],
            "add_static_route": ["ip route add dst-address={DISTANT_NETWORK} gateway={INTERFACE_PREFIX}{INTERFACE}"],
            "stop": []
        },
        "routing_stack": {
            "start": [],
            "add_rip_route": [

            ],
            "add_ospf_route": {
                "add_interface": ["routing ospf instance add name={INSTANCE_NAME} version=2 router-id={ROUTER_ID}"],
                "add_area": [
                    "routing ospf area add name={AREA_NAME} area-id=0.0.0.0 instance={INSTANCE_NAME}",
                    "routing ospf interface-template add networks={DISTANT_NETWORK} area={AREA_NAME}"
                ],
            },
            "add_bgp_route": [

            ],
            "add_mpls_route": [

            ],
            "stop": []
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
        "network_stack": "iproute2",
        "routing_stack": "frr",
        "interface_prefix": "eth",
        "interfaces_start_at": 0,
        "image_path": "/home/julien/Programmation/vm/SONiC/sonic-vs-202411.img"
    },
    'VyOS': {
        "input_ready": ":~",
        "trigger_sequence": None,
        "login": "vyos",
        "password": "vyos",
        "network_stack": "iproute2",
        "routing_stack": "frr",
        "interface_prefix": "eth",
        "interfaces_start_at": 0,
        "image_path": "/home/julien/Programmation/vm/VyOS/vyos-2025.04.04-0018-rolling-generic-amd64.iso"
    }
}