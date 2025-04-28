import subprocess
from glob import glob

from src.constants import EXPERIMENT_NAME, EXPERIMENT_DURATION, ROUTER_VCPU, ROUTER_RAM, ROUTER_NIC

match EXPERIMENT_NAME:
    case 'rrul':
        real_experiment_name = 'Realtime Response Under Load'
    case _:
        real_experiment_name = EXPERIMENT_NAME

paths = []

for path in glob('shared/*/*.flent.gz'):
    paths.append('-i')
    paths.append(path)

plots = [
    ('box_totals', 'Box plot of totals', 0),
    ('icmp_cdf', 'ICMP CDF', 13)
]

for plot, plot_title, note_adjustment in plots:
    fig_note_line1 = f'{EXPERIMENT_DURATION}s, NIC {ROUTER_NIC}'
    fig_note_line2 = f'{ROUTER_VCPU} CPU, {ROUTER_RAM}Mb RAM'

    subprocess.Popen([
        'flent',
        #'--new-gui-instance',
        '-o', f'plots/{plot}.png',
        '-p', plot,
        #'--scale-mode',
        '--log-scale-y', 'log10',
        '--skip-missing-series',
        #'--legend-title', 'OS',
        '--no-title',
        #'--override-title', f'{real_experiment_name}\n{plot_title}',
        '--figure-note', (' ' * (190 - note_adjustment - len(fig_note_line1))) + fig_note_line1 + '\n' + (' ' * (190 - note_adjustment - len(fig_note_line2))) + fig_note_line2,
        '--filter-regexp', '__.*',
        '--filter-regexp', 'run_[0-9]+',
        '--filter-regexp', 'Ping \\(ms\\) --',
        '--filter-regexp', 'ICMP - ',
        '--filter-regexp', '(?:[0-9]{1,3}\\.){3}[0-9]{1,3}',
        '--no-annotation',
        #'--figure-width=9',
        #'--figure-height=6',
        '--figure-dpi=300',
        '--fallback-layout'
    ] + paths)