#!/usr/bin/env python3
import argparse
import json
import os

from src.utils import sanitize_string
from src_case_generator.config import config
from src_case_generator.operating_systems import operating_systems
from src_case_generator.resources import resources
from src_case_generator.nics import nics
from src_case_generator.network_protocols import protocols
from src_case_generator.tests import tests


def main(generate_templates: bool):
    case_counter = 0
    seconds_counter = 0

    for os_name, os_config in operating_systems.items():
        for test_name, test in tests.items():
            experiment_duration = 30 + 5

            for actual_test in test:
                experiment_duration += actual_test['fire_at'] + actual_test['duration']

            for resources_name, resources_config in resources.items():
                for nic_name, nic in nics.items():
                    match os_config['routing_stack']:
                        case None:
                            usable_protocols = { 'static': protocols['static'] }
                        case 'gobgp':
                            usable_protocols = {'static': protocols['static'], 'BGP': protocols['BGP']}
                        case _ :
                            usable_protocols = protocols

                    for protocol_name, associated_topologies in usable_protocols.items():
                        for associated_topology in associated_topologies:
                            topology_name, topology = associated_topology(os_name=os_name, resources_config=resources_config, nic=nic)

                            directory = f'experiments/{os_name}/{test_name}/{resources_name}/{nic_name}'
                            file_name = f'{sanitize_string(topology_name)}-{os_name}-{resources_name}-{nic_name}-{protocol_name}.json'
                            file_path = os.path.join(directory, file_name)

                            if generate_templates:
                                template = generate_template(
                                    os_name=os_name,
                                    os_config=os_config,
                                    test_name=test_name,
                                    test=test,
                                    resources_name=resources_name,
                                    nic_name=nic_name,
                                    protocol_name=protocol_name,
                                    topology_name=topology_name,
                                    topology=topology
                                )
                                template_json = json.dumps(template, indent=2)

                                os.makedirs(directory, exist_ok=True)
                                file = open(file_path, 'w+')
                                file.write(template_json)

                                seconds_counter += experiment_duration
                                case_counter += 1

                                print(f'Wrote template to: {file_path}')
                            else:
                                print(f'-i {file_path} ', end='')

    if generate_templates:
        print(f'Generated {case_counter} templates')
        print(f'Should take about {seconds_counter/60/60} hours to bench')

def generate_template(os_name: str, os_config: dict, test_name: str, test: dict, resources_name: str, nic_name: str, protocol_name: str, topology_name: str, topology) -> dict:
    os_config_copy = os_config.copy()

    if callable(os_config['interface_prefix']):
        os_config_copy['interface_prefix'] = os_config['interface_prefix'](nic=nic_name)

    return {
      'experiment_name': f'{topology_name} {os_name} {test_name} {resources_name} {nic_name} {protocol_name}',
      'plot_legend_when_merged': f'{os_name} {test_name} {resources_name} {nic_name} {protocol_name}',
      'config': config,
      'network': topology,
      'tests': test,
      'os_list': {
        os_name: os_config_copy
      }
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='router-os-benchmark',
        description='Generate all possible cases within what is specified',
    )

    parser.add_argument('-o', '--os', dest='os')
    parser.add_argument('-t', '--test', dest='test', choices=tests.keys())
    parser.add_argument('-r', '--resources', dest='resources', choices=resources.keys())
    parser.add_argument('-n', '--nic', dest='nic', choices=nics.keys())
    parser.add_argument('-p', '--protocol', dest='protocol', choices=protocols.keys())

    parser.add_argument('--generate-templates', dest='generate_templates', action='store_true', help="Generate experiment templates")
    args = parser.parse_args()

    if args.os is not None:
        operating_systems = {
            args.os: operating_systems[args.os]
        }

    if args.test is not None:
        tests = {
            args.test: tests[args.test]
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