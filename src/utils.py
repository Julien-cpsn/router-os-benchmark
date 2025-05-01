import glob
import os

def sanitize_string(string: str) -> str:
    return (string
        .replace(' ', '-')
        .replace('/', '_')
        .replace('\\', '_')
        .replace('\n', '')
        .replace('\t', '')
        .replace('\r', '')
    )

def network_from_ip(ip: str) -> str:
    parts = ip.split('.')[:-1]
    parts += '0'
    return '.'.join(parts)

def change_last_ip_class(ip: str, new_last_class: str) -> str:
    parts = ip.split('.')[:-1]
    parts += new_last_class
    return '.'.join(parts)

def get_experiment_test_results(experiment_name: str, test_name: str) -> list[str]:
    path = f'shared/{experiment_name}/{test_name}'

    if not os.path.exists(path):
        print(f'Folder "{path}" does not exist')
        exit(1)

    paths = glob.glob(f'{path}/*.flent.gz') + glob.glob(f'{path}/*/*.flent.gz')

    if len(paths) == 0:
        print(f'Folder "{path}" has no test results')
        exit(1)

    return paths