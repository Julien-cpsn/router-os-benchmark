import glob
import itertools
import os

from src_case_generator.operating_systems import operating_systems
from src_case_generator.resources import resources
from src_case_generator.nics import nics
from src_case_generator.network_protocols import protocols
from src_case_generator.tests import tests


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
        print(f'\nFolder "{path}" does not exist')
        exit(1)

    paths = glob.glob(f'{path}/*.flent.gz') + glob.glob(f'{path}/*/*.flent.gz')

    if len(paths) == 0:
        print(f'\nFolder "{path}" has no test results')
        exit(1)

    return paths


def extract_and_sort_common_parts(strings: list[str]) -> tuple[list, list]:
    if len(strings) == 1:
        return [], [strings[0]]

    word_sets = []
    for string in strings:
        # Convert to lowercase and split by whitespace
        words = set(string.replace('_', ' ').split())
        word_sets.append(words)

    # Find words common to all strings
    common_words = set.intersection(*word_sets)

    # Find all unique words across all strings
    all_words = set.union(*word_sets)

    # Non-common words are words that appear in at least one string but not in all strings
    non_common_words = all_words - common_words

    return sorted(list(common_words), key=lambda x: sort_word(x)), sorted(list(non_common_words), key=lambda x: sort_word(x))

def count_lowercase_char(string: str) -> int:
    count = 0

    for i in string:
        if i.islower():
            count = count + 1

    return count

def prepare_keys(keys: dict) -> list[str]:
    return list(itertools.chain.from_iterable([key.split('_') for key in keys.keys()]))

def sort_word(word: str) -> int:
    os_keys = prepare_keys(operating_systems)
    tests_keys = prepare_keys(tests)
    resources_keys = prepare_keys(resources)
    nics_keys = prepare_keys(nics)
    protocols_keys = prepare_keys(protocols)

    if word in os_keys:
        return 0 + os_keys.index(word)
    elif word in tests_keys:
        return 10 + tests_keys.index(word)
    elif word in resources_keys:
        return 20 + resources_keys.index(word)
    elif word in nics_keys:
        return 30 + nics_keys.index(word)
    elif word in protocols_keys:
        return 40 + protocols_keys.index(word)
    else:
        return 50