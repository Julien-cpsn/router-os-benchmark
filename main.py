#!/usr/bin/env python3
import argparse

import src.run
import src.plot
import src.clean
from src.constants import Constants
from src.experiments_file import load_experiment_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='router-os-benchmark',
        description='Benchmark and plot performances for router and network OSes',
    )

    parser.add_argument('command', choices=['run', 'plot', 'clean'])
    parser.add_argument('-i', '--input', dest='experiment_files', type=argparse.FileType('r'), action='append')
    args = parser.parse_args()

    experiment_list: list[Constants] = []

    for experiment_file in args.experiment_files:
        experiment_data = load_experiment_data(experiment_file)
        experiment_list.append(Constants(experiment_data))

    match args.command:
        case 'run':
            for constants in experiment_list:
                src.run.main(constants)
        case 'plot':
            src.plot.main(experiment_list)
        case 'clean':
            for constants in experiment_list:
                src.clean.main(constants)