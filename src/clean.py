import glob
import os

from src.constants import Constants
from src.utils import get_experiment_test_results


def main(constants: Constants):
    print(f'Cleaning {constants.EXPERIMENT_NAME}')

    for file in get_experiment_test_results(experiment_name=constants.EXPERIMENT_NAME, test_name='*'):
        print(f'Removing file: {file}')
        os.remove(file)