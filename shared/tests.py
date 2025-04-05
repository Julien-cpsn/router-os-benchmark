import json
from logging import Logger
from typing import Optional, Dict

from router_tester import RouterThroughputTester
from logger import setup_logger, get_time


def many_tests(test_list_path: str, guest_image: str, number_runs: int, duration: int, access_cli: bool, use_json_output: bool, verbosity: int, test_logger: Logger) -> Optional[dict]:
    """
    Many router OS tests

    :param test_list_path:
    :param guest_image:
    :param number_runs:
    :param duration:
    :param access_cli:
    :param use_json_output:
    :param verbosity:
    :param test_logger:
    :return:
    """
    json_output = {}

    test_logger.info('Opening test list file')
    test_list_file = open(test_list_path, 'r')
    test_list: dict[str, dict[str, str]] = json.load(test_list_file)

    if not isinstance(test_list, Dict):
        test_logger.error("Test file is not a dict[str, str]")
        exit(1)

    test_time = get_time(len(test_list), number_runs, duration)
    test_logger.info(f'Test will last {test_time}')

    for name, params in test_list.items():
        router_image = params['image']
        config = params['config']

        single_output = single_test(name, router_image, config, guest_image, number_runs, duration, access_cli, use_json_output, verbosity, test_logger, True)

        json_output[name] = {
            'average': calculate_average(single_output),
            'runs': single_output
        }

        with open(f'results/{name}/result.json', 'w') as f:
            f.write(json.dumps(json_output[name], indent=2))

    with open('results/result_global.json', 'w') as f:
        f.write(json.dumps(json_output, indent=2))

    return json_output

def single_test(name: str, router_image: str, config: str, guest_image: str, number_runs: int, duration: int, access_cli: bool, use_json_output: bool, verbosity: int, test_logger: Logger, many: bool = False) -> list:
    """
    Single router OS test

    :param name:
    :param router_image:
    :param config:
    :param guest_image:
    :param number_runs:
    :param duration:
    :param access_cli:
    :param use_json_output:
    :param verbosity:
    :param test_logger:
    :return:
    """
    results = []

    if not many:
        test_time = get_time(1, number_runs, duration)
        test_logger.info(f'Test will last {test_time}')

    test_logger.info(f'Starting {name} test')

    logger = setup_logger(f'TEST {name.upper()}', verbosity)

    for run_number in range(1, number_runs+1):
        logger.info(f'{name} run {run_number}')

        run_logger = setup_logger(f'TEST {name.upper()} RUN {run_number}', verbosity)
        tester = RouterThroughputTester(name, router_image, config, guest_image, run_number, run_logger)
        result = tester.run_test(duration, access_cli)

        if use_json_output:
            if not many:
                print(json.dumps(result, indent=2))
        else:
            print(f"--- {name} run {run_number} ---")
            for key, value in result.items():
                print(f"{key}: {value}")

        results.append(result)

    return results

def calculate_average(results: list) -> dict:
    throughput_mbps_sum = 0
    jitter_ms_sum = 0
    lost_percent_sum = 0

    for result in results:
        throughput_mbps_sum += result['throughput_mbps']
        jitter_ms_sum += result['jitter_ms']
        lost_percent_sum += result['lost_percent']

    throughput_mbps_avg = throughput_mbps_sum / len(results)
    jitter_ms_avg = jitter_ms_sum / len(results)
    lost_percent_avg = lost_percent_sum / len(results)

    return {
        'throughput_mbps': throughput_mbps_avg,
        'jitter_ms': jitter_ms_avg,
        'lost_percent': lost_percent_avg,
    }