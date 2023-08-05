import os
import sys
import glob
import numpy as np

sys.path.append(os.getcwd())

import matplotlib.pyplot as plt
from PyExpUtils.models.ExperimentDescription import loadExperiment, ExperimentDescription
from PyExpUtils.results.results import loadResults, getBest, splitOverParameter

from PyExpPlotting.matplot import save, setDefaultConference
from PyExpPlotting.distributions import parameterStudyAlgs, plot, stacked, stackedAlgs

setDefaultConference('icml')

colors = {
    'QLearning': 'blue',
    'SBEED': 'black',
    'QRC': 'red',
}

class Model(ExperimentDescription):
    def __init__(self, d, path):
        super().__init__(d, path, save_key='tests/results/{name}/{agent}')
        self.agent = d['agent']
        self.problem = d['problem']

if __name__ == '__main__':
    f, ax = plt.subplots(1)

    alg_results = []
    exp_paths = glob.glob('tests/experiments/example/CartPole/*.json')
    for exp_path in exp_paths:
        exp = loadExperiment(exp_path, Model)

        results = loadResults(exp, 'returns.csv')
        alg_results.append(results)

    parameterStudyAlgs(alg_results, ax, 'optimizer.alpha', np.mean, {
        'colors': colors,
        'prefer': 'big',
        'alg_spacing': 0.25,
        'hist': True,
        'process_y_ticks': np.log2,
        'highlight_top': True,
    })

    save('tests/', 'test', height_ratio=2.0)
