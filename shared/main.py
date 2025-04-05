#!/usr/bin/env python3

import argparse
import json

from logger import setup_logger
from tests import many_tests, single_test


def main():
    test_logger = setup_logger('TEST', verbosity)

    if test_type == 'many':
        os_list = args.os_list
        output = many_tests(os_list, guest_image, number_runs, duration, access_cli, use_json_output, verbosity, test_logger)

        if use_json_output:
            output = json.dumps(output, indent=2)
            print(output)
    elif test_type == 'single':
        name, router_image, config = args.name, args.router_image, args.config
        single_test(name, router_image, config, guest_image, number_runs, duration, access_cli, use_json_output, verbosity, test_logger)
    else:
        return

if __name__ == '__main__':
    # Parser for command-line arguments
    parser = argparse.ArgumentParser(description='Router OS Network Throughput Tester')

    test_type_parser = parser.add_subparsers(dest='test_type', help='Test type', required=True)

    single_test_parser = test_type_parser.add_parser('single', help='Single Router OS test')
    single_test_parser.add_argument('name', help='Router OS name')
    single_test_parser.add_argument('router_image', help='Path to router OS disk image')
    single_test_parser.add_argument('config', help='Network stack config. Either use "unix" or put configuration commands')

    many_tests_parser = test_type_parser.add_parser('many', help='Many Router OS test')
    many_tests_parser.add_argument('os_list', help='Path to the JSON test list')

    parser.add_argument('guest_image', help='Path to router guest disk image')
    parser.add_argument('--runs', '-r', type=int, default=1, help='Number of test runs')
    parser.add_argument('--duration', '-d', type=int, default=10, help='iPerf3 test duration')
    parser.add_argument('--cli', '-c', dest='access_cli', default=False, action='store_true', help='Access CLI before running each test')
    parser.add_argument('--json', '-j', dest='use_json_output', default=False, action='store_true', help='Output JSON')
    parser.add_argument('--verbose', '-v', dest='verbosity', default=0, action='count', help='Change verbosity level')
    args = parser.parse_args()

    # Set global variables
    test_type, guest_image, verbosity, number_runs, duration, access_cli, use_json_output = args.test_type, args.guest_image, args.verbosity, args.runs, args.duration, args.access_cli, args.use_json_output

    main()