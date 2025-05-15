import os
import subprocess
from typing import Optional

from src.constants import Constants
from src.types import Test
from src.utils import get_experiment_test_results, sanitize_string, extract_and_sort_common_parts, count_lowercase_char, \
    sort_word

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

def main(experiment_list: list[Constants], log_scale: bool, show_title: bool, hide_note: bool, remove_legends: list[str], remove_common_legend: bool):
    experiments: dict[Constants, dict[Test, list[str]]] = {}
    notes = None

    if len(experiment_list) == 1:
        constants = experiment_list[0]
        print(f'Plotting {constants.EXPERIMENT_NAME}')
        directory = constants.EXPERIMENT_NAME
        experiments[constants] = extract_data(constants)
    else:
        print(f'Merging ', end='')

        plot_legends = [constants.PLOT_LEGEND_WHEN_MERGED for constants in experiment_list]
        common_words, non_common_words = extract_and_sort_common_parts(plot_legends)
        common_words_str = ' '.join(common_words)
        non_common_words_str = ' '.join(non_common_words)
        directory = f'merged_{sanitize_string(non_common_words_str)}_{sanitize_string(common_words_str)}'

        for index, constants in enumerate(experiment_list):
            print(constants.PLOT_LEGEND_WHEN_MERGED, end='')

            experiments[constants] = extract_data(constants)

            if index != len(experiment_list) - 1:
                print(', ', end='')

        if remove_common_legend:
            remove_legends += sorted(list(common_words), key=lambda x: sort_word(x))

        if not hide_note:
            notes = common_words

    print('\n')

    plot_experiments(experiments, directory, notes, log_scale, show_title, remove_legends)

def extract_data(constants: Constants) -> dict[Test, list[str]]:
    data = {}

    for test in constants.TESTS:
        if test.name not in data:
            data[test] = []

        test_results = get_experiment_test_results(experiment_name=constants.EXPERIMENT_NAME, test_name=test.name)
        data[test] += test_results

    return data

def adjusted_note(notes: list[str], note_adjustment: int) -> str:
    lines = []
    for index, line in enumerate(notes):
        spaces_count = 196 - note_adjustment - len(line) + int(count_lowercase_char(line) / 3)

        if index == 0:
            spaces_count -= 1

        lines.append(' ' * spaces_count + line + '\n')

    return ''.join(lines)

def plot_experiments(experiments: dict[Constants, dict[Test, list[str]]], plot_directory_name: str, notes: Optional[list[str]], log_scale: bool, show_title: bool, remove_legends: list[str]):
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
        ('box_totals', 'Box plot of totals', 0),
        ('icmp_cdf', 'ICMP CDF', 13)
    ]

    extensions = [
        'svg',
        'png'
    ]

    for test_name, files in tests_to_plot.items():
        print(f'Plotting {test_name}')
        for plot, plot_title, note_adjustment in plots:
            additional_arguments = []

            if notes is not None:
                figure_note = adjusted_note(notes, note_adjustment)
                additional_arguments += ['--figure-note', figure_note]

            if log_scale:
                additional_arguments += ['--log-scale-y', 'log10']

            if not show_title:
                additional_arguments += ['--no-title']

            for remove_legend in remove_legends:
                additional_arguments += ['--filter-regexp', remove_legend.lstrip().rstrip() + '\\s?']

            for extension in extensions:
                plot_directory =f'plots/{plot_directory_name}/{test_name}'
                os.makedirs(plot_directory, exist_ok=True)
                plot_path = f'{plot_directory}/{plot}.{extension}'

                subprocess.Popen([
                    'flent',
                    #'--new-gui-instance',
                    '-o', plot_path,
                    '-p', plot,
                    #'--scale-mode',
                    '--skip-missing-series',
                    #'--legend-title', 'OS',
                    #'--override-title', f'{real_experiment_name}\n{plot_title}',
                    '--filter-regexp', '_',
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