import os
import subprocess

from src.constants import Constants
from src.types import Test
from src.utils import get_experiment_test_results, sanitize_string

"""
COLORS = [
    '#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#d62728',
    '#9467bd',
    '#8c564b',
    '#e377c2',
    #'#7f7f7f',
    '#bcbd22',
    '#17becf',
    '#aec7e8',
    '#ffbb78',
    '#98df8a',
    '#ff9896',
    '#c5b0d5'
]

def get_colors(files: list) -> str:
    number_of_colors = int(len(files) / 2)
    random.shuffle(COLORS)
    colors = [f"'{color}'" for color in COLORS[:number_of_colors]]

    return ','.join(colors)
"""

def main(experiment_list: list[Constants], log_scale: bool, show_title: bool, remove_legends: list[str]):
    experiments: dict[Constants, dict[Test, list[str]]] = {}

    if len(experiment_list) == 1:
        constants = experiment_list[0]
        print(f'Plotting {constants.EXPERIMENT_NAME}')
        directory = constants.EXPERIMENT_NAME
        experiments[constants] = extract_data(constants)
    else:
        print(f'Merging ', end='')

        directory = 'merged'
        for constants in sorted(experiment_list, key=lambda c: c.PLOT_LEGEND_WHEN_MERGED):
            directory += f'-{sanitize_string(constants.PLOT_LEGEND_WHEN_MERGED)}'

        for index, constants in enumerate(experiment_list):
            print(constants.PLOT_LEGEND_WHEN_MERGED, end='')

            experiments[constants] = extract_data(constants)

            if index != len(experiment_list) - 1:
                print(', ', end='')

    print('\n')

    plot_experiments(experiments, directory, log_scale, show_title, remove_legends)

def extract_data(constants: Constants) -> dict[Test, list[str]]:
    data = {}

    for test in constants.TESTS:
        if test.name not in data:
            data[test] = []

        test_results = get_experiment_test_results(experiment_name=constants.EXPERIMENT_NAME, test_name=test.name)
        data[test] += test_results

    return data

def plot_experiments(experiments: dict[Constants, dict[Test, list[str]]], plot_directory_name: str, log_scale: bool, show_title: bool, remove_legends: list[str]):
    legends_to_replace: list[str] = []
    tests_to_plot: dict[str, list[str]] = {}

    for constants, tests in experiments.items():
        replace_legend = constants.PLOT_LEGEND_WHEN_MERGED

        if len(experiments) > 1:
            if replace_legend is None:
                print(f'Since experiment merge is happening, please provide "plot_legend_when_merged" for experiment {constants.EXPERIMENT_NAME}')
                exit(1)
            else:
                legends_to_replace.append(f'--replace-legend={constants.EXPERIMENT_NAME}={replace_legend}')
        else:
            if replace_legend is not None:
                print('Attribute "plot_legend_when_merged" will be ignored since no merge is happening')

        for test, paths in tests.items():
            if test.name not in tests_to_plot:
                tests_to_plot[test.name] = []

            for path in paths:
                tests_to_plot[test.name].append('-i')
                tests_to_plot[test.name].append(path)

    plots = [
        ('box_totals', 'Box plot of totals'),
        ('icmp_cdf', 'ICMP CDF')
    ]

    extensions = [
        'svg',
        'png'
    ]

    for test_name, files in tests_to_plot.items():
        print(f'Plotting {test_name}')
        for plot, plot_title in plots:
            for extension in extensions:
                #fig_note_line1 = f'{EXPERIMENT_DURATION}s, NIC {ROUTER_NIC}'
                #fig_note_line2 = f'{ROUTER_VCPU} vCPU, {ROUTER_RAM}Mb RAM'

                plot_directory =f'plots/{plot_directory_name}/{test_name}'
                os.makedirs(plot_directory, exist_ok=True)
                plot_path = f'{plot_directory}/{plot}.{extension}'

                additional_arguments = []

                if log_scale:
                    additional_arguments += ['--log-scale-y', 'log10']

                if not show_title:
                    additional_arguments += ['--no-title']

                for remove_legend in remove_legends:
                    additional_arguments += ['--filter-regexp', remove_legend]

                subprocess.Popen([
                    'flent',
                    #'--new-gui-instance',
                    '-o', plot_path,
                    '-p', plot,
                    #'--scale-mode',
                    '--skip-missing-series',
                    #'--legend-title', 'OS',
                    #'--override-title', f'{real_experiment_name}\n{plot_title}',
                    #'--figure-note', (' ' * (190 - note_adjustment - len(fig_note_line1))) + fig_note_line1 + '\n' + (' ' * (190 - note_adjustment - len(fig_note_line2))) + fig_note_line2,
                    '--filter-regexp', '__.*',
                    '--filter-regexp', '.* - ',
                    '--filter-regexp', 'Ping \\(ms\\) --',
                    '--filter-regexp', 'ICMP - ',
                    '--filter-regexp', '(?:[0-9]{1,3}\\.){3}[0-9]{1,3}',
                    #'--colours', get_colors(files),
                    '--no-annotation',
                    '--no-markers',
                    #'--no-matplotlibrc',
                    '--no-hover-highlight',
                    #'--figure-width=9',
                    #'--figure-height=6',
                    #'--figure-dpi=300',
                    '--fallback-layout'
                ] + files + legends_to_replace + additional_arguments)

                print(f'Plot {plot_title}: {os.getcwd()}/{plot_path}')