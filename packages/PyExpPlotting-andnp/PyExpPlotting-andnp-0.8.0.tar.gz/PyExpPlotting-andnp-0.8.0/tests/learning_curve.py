import os
import sys
import glob

sys.path.append(os.getcwd())

import matplotlib.pyplot as plt
from PyExpUtils.models.ExperimentDescription import loadExperiment, ExperimentDescription
from PyExpUtils.results.results import loadResults

from PyExpPlotting.matplot import save, setDefaultConference
from PyExpPlotting.learning_curves import plotBest

setDefaultConference('icml')

class Model(ExperimentDescription):
    def __init__(self, d, path):
        super().__init__(d, path, save_key='tests/results/{name}/{agent}')
        self.agent = d['agent']
        self.problem = d['problem']

if __name__ == '__main__':
    f, ax = plt.subplots(1)

    exp_paths = glob.glob('tests/experiments/example/CartPole/*.json')
    for exp_path in exp_paths:
        exp = loadExperiment(exp_path, Model)

        results = loadResults(exp, 'returns.csv')

        plotBest(results, ax, {
            'y_label': 'return',
            'x_label': 'steps',
        })

    save('tests/', 'test', height_ratio=0.75)
