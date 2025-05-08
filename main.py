#!/usr/bin/env python3
import argparse
import os
from glob import glob

import src.run
import src.plot
import src.clean
from src.constants import Constants
from src.experiments_file import load_experiment_data

def main():
    parser = argparse.ArgumentParser(
        prog='router-os-benchmark',
        description='Benchmark and plot performances for router and network OSes',
    )
    subparsers = parser.add_subparsers(help='Action', dest='command')

    run_parser = subparsers.add_parser('run')

    plot_parser = subparsers.add_parser('plot')
    plot_parser.add_argument('--log-scale', dest='log_scale', action='store_true', help="Use log 10 scale")
    plot_parser.add_argument('--show-title', dest='show_title', action='store_true', help="Show plot title")
    plot_parser.add_argument('--remove-legend', dest='remove_legends', action='append', help="Regex in legend to remove")

    clean_parser = subparsers.add_parser('clean')

    parser.add_argument('-d', '--directory', dest='experiment_directories', type=dir_path, action='append', help="Directory containing experiment files")
    parser.add_argument('-R', '--recursive', dest='recursive', action='store_true', help="Find files recursively. Only works with directories.")
    parser.add_argument('-i', '--input', dest='experiment_files', type=argparse.FileType('r'), action='append', help="Input experiment files")

    args = parser.parse_args()

    experiment_files = []

    if args.experiment_directories is not None:
        for directory in args.experiment_directories:
            path = directory + ('**' if args.recursive else '') + '/*.json'
            for file_path in sorted(glob(path, recursive=args.recursive)):
                experiment_files.append(open(file_path, 'r'))

    if args.experiment_files is not None:
        for experiment_file in args.experiment_files:
            experiment_files.append(experiment_file)

    experiment_list: list[Constants] = []

    for experiment_file in experiment_files:
        experiment_data = load_experiment_data(experiment_file)
        experiment_list.append(Constants(experiment_data))

    if len(experiment_list) == 0:
        print('No experiment data provided. Please use "-i" or "-d".')
        exit(1)

    match args.command:
        case 'run':
            for constants in experiment_list:
                src.run.main(constants)
        case 'plot':
            remove_legends = args.remove_legends if args.remove_legends is not None else []

            src.plot.main(experiment_list, args.log_scale, args.show_title, remove_legends)
        case 'clean':
            for constants in experiment_list:
                src.clean.main(constants)

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

if __name__ == '__main__':
    main()