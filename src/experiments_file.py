import json
import jsonschema
from loguru import logger

schema = {
    '$schema': 'http://json-schema.org/draft-07/schema#',
    'type': 'object',
    'required': ['experiment_name', 'plot_legend_when_merged', 'config', 'network', 'tests', 'os_list'],
    'properties': {
        'experiment_name': {'type': 'string'},
        'plot_legend_when_merged': {'type': ['string', 'null']},
        'config': {
            'type': 'object',
            'required': ['project_name', 'template_prefix', 'guest_image_path', 'gns3'],
            'properties': {
                'project_name': {'type': 'string'},
                'template_prefix': {'type': 'string'},
                'guest_image_path': {'type': 'string'},
                'gns3': {
                    'type': 'object',
                    'properties': {
                        'url': {'type': 'string', 'format': 'uri'},
                        'server_username': {'type': 'string'},
                        'server_password': {'type': 'string'},
                    },
                    'required': ['url', 'server_username', 'server_password'],
                },
            },
        },
        'network': {
            'type': 'object',
            'required': ['nodes', 'links'],
            'properties': {
                'nodes': {
                    'type': 'object',
                    'additionalProperties': {
                        'type': 'object',
                        'required': ['type', 'vcpu', 'ram'],
                        'properties': {
                            'type': {'enum': ['guest', 'router']},
                            'vcpu': {'type': 'integer', 'minimum': 1},
                            'ram': {'type': 'integer', 'minimum': 1},
                            'os': {'type': ['string', 'null']},
                            'ip': {'type': 'string', 'format': 'ip-address'},
                            'nic': {'enum': ['e1000', 'e1000e', 'i82550', 'i82551', 'i82551', 'i82557a', 'i82557b','i82557c', 'i82558a', 'i82559a', 'i82559b', 'i82559c', 'i82559er', 'i82562', 'i82801', 'igb', 'ne2k_pci', 'pcnet', 'rocker', 'rtl8139', 'virtio-net-pci']},
                            'adapters': {'type': 'integer', 'minimum': 1},
                            'ips': {
                                'type': 'array',
                                'required': ['adapter', 'ip'],
                                'additionalProperties': {
                                    'adapter': {'type': 'integer', 'minimum': 0},
                                    'ip': {'type': 'string', 'format': 'ip-address'},
                                }
                            },
                            'routes': {
                                'type': 'object',
                                'required': ['RIP', 'OSPF', 'BGP', 'MPLS'],
                                'properties': {
                                    'static': {
                                        'type': 'array',
                                        'required': ['distant_network', 'via'],
                                        'additionalProperties': {
                                            'distant_network': {'type': 'string', 'format': 'ip-address'},
                                            'via': {'type': 'string', 'format': 'ip-address'}
                                        }
                                    },
                                    'RIP': {'type': 'array'},
                                    'OSPF': {'type': 'array'},
                                    'BGP': {'type': 'array'},
                                    'MPLS': {'type': 'array'}
                                }
                            }
                        },
                        'if': {'properties': {'type': {'const': 'router'}}},
                        'then': {'required': ['os', 'nic', 'adapters', 'ips', 'routes']},
                        'else': {'required': ['ip']},
                    }
                },
                'links': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'required': ['node_a', 'adapter_a', 'node_b', 'adapter_b'],
                        'properties': {
                            'node_a': {'type': 'string'},
                            'adapter_a': {'type': 'integer', 'minimum': 0},
                            'node_b': {'type': 'string'},
                            'adapter_b': {'type': 'integer', 'minimum': 0},
                        }
                    }
                }
            },
        },
        'tests': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'test': {'enum': ['bursts', 'bursts_11e', 'cisco_5tcpup', 'cisco_5tcpup_2udpflood', 'cubic_bbr', 'cubic_cdg', 'cubic_dctcp', 'cubic_ledbat', 'cubic_ledbat_1', 'cubic_reno', 'cubic_westwood', 'dashtest', 'dslreports_8dn', 'http', 'http-1down', 'http-1up', 'http-rrul', 'iterated_bidirectional', 'ledbat_cubic_1', 'ping', 'qdisc-stats', 'reno_cubic_westwood_cdg', 'reno_cubic_westwood_ledbat', 'reno_cubic_westwood_lp', 'rrul', 'rrul46', 'rrul46compete', 'rrul_100_up', 'rrul_50_down', 'rrul_50_up', 'rrul_be', 'rrul_be_iperf', 'rrul_be_nflows', 'rrul_cs8', 'rrul_icmp', 'rrul_noclassification', 'rrul_prio', 'rrul_torrent', 'rrul_up', 'rrul_var', 'rtt_fair', 'rtt_fair4be', 'rtt_fair6be', 'rtt_fair_up', 'rtt_fair_var', 'rtt_fair_var_down', 'rtt_fair_var_mixed', 'rtt_fair_var_up', 'sctp_vs_tcp', 'tcp_12down', 'tcp_12up', 'tcp_1down', 'tcp_1up', 'tcp_1up_noping', 'tcp_2down', 'tcp_2up', 'tcp_2up_delay', 'tcp_2up_square', 'tcp_2up_square_westwood', 'tcp_4down', 'tcp_4up', 'tcp_4up_squarewave', 'tcp_50up', 'tcp_6down', 'tcp_6up', 'tcp_8down', 'tcp_8up', 'tcp_bidirectional', 'tcp_download', 'tcp_ndown', 'tcp_nup', 'tcp_upload', 'tcp_upload_1000', 'tcp_upload_prio', 'udp_flood', 'udp_flood_var_up', 'udp_flood_var_up_stagger', 'voip', 'voip-1up', 'voip-rrul']},
                    'fire_at': {'type': 'integer', 'minimum': 0},
                    'duration': {'type': 'integer', 'minimum': 1},
                    'from': {'type': 'string'},
                    'to': {'type': 'string'},
                },
                'required': ['name', 'fire_at', 'duration', 'from', 'to'],
            }
        },
        'os_list': {
            'type': 'object',
            'additionalProperties': {
                'type': 'object',
                'required': ['input_ready', 'login', 'password', 'trigger_sequence', 'network_stack', 'routing_stack', 'interface_prefix', 'interfaces_start_at', 'image_path'],
                'properties': {
                    'input_ready': {'type': 'string'},
                    'trigger_sequence': {'type': ['string', 'null']},
                    'login': {'type': ['string', 'null']},
                    'password': {'type': ['string', 'null']},
                    'network_stack': {
                        'oneOf': [
                            {
                                'type': ['string'],
                                'enum': ['iproute2', 'freebsd', 'openbsd']
                            },
                            {
                                'type': 'object',
                                'required': ['start', 'add_ip_address', 'add_static_address', 'stop'],
                                'properties': {
                                    'start': {'type': 'array', 'additionalProperties': {'type': 'string'}},
                                    'add_ip_address': {'type': 'array'},
                                    'add_static_route': {'type': 'array'},
                                    'stop': {'type': 'array', 'additionalProperties': {'type': 'string'}},
                                },
                            }
                        ],
                    },
                    'routing_stack': {
                        'oneOf': [
                            {
                                'type': 'null'
                            },
                            {
                                'type': ['string'],
                                'enum': ['frr', 'quagga', 'bird2', 'holo', 'gobgp']
                            },
                            {
                                'type': 'object',
                                'required': ['start', 'add_rip_route', 'stop'],
                                'properties': {
                                    'start': {'type': 'array', 'additionalProperties': {'type': 'string'}},
                                    'add_rip_route': {'type': 'array'},
                                    'add_ospf_route': {
                                        'type': 'object',
                                        'required': ['add_interface', 'add_area'],
                                        'properties': {
                                            'add_interface': {'type': 'array', 'additionalProperties': {'type': 'string'}},
                                            'add_area': {'type': 'array', 'additionalProperties': {'type': 'string'}},
                                        }
                                    },
                                    'stop': {'type': 'array', 'additionalProperties': {'type': 'string'}},
                                },
                            }
                        ],
                    },
                    'interface_prefix': {'type': 'string'},
                    'interfaces_start_at': {'type': 'integer', 'minimum': 0},
                    'image_path': {'type': 'string'}
                },
            }
        },
    },
}


def load_experiment_data(experiment_file) -> dict:
    json_data = json.load(experiment_file)

    try:
        jsonschema.validate(instance=json_data, schema=schema)
    except Exception as e:
        logger.error(e)
        exit(1)

    return json_data