import os
import sys

sys.path.append(os.getcwd())

import matplotlib.pyplot as plt
from PyExpUtils.models.ExperimentDescription import loadExperiment, ExperimentDescription
from PyExpUtils.results.results import loadResults

from PyExpPlotting.tools import findExperiments
from PyExpPlotting.matplot import save, setDefaultConference
from PyExpPlotting.learning_curves import plotBest

setDefaultConference('icml')

class Model(ExperimentDescription):
    def __init__(self, d, path):
        super().__init__(d, path, save_key='tests/results/{name}/{agent}')
        self.agent = d['agent']
        self.problem = d['problem']

if __name__ == '__main__':

    exps = findExperiments(key='{domain}')
    for domain in exps:
        print(domain)
        f, ax = plt.subplots(1)
        for exp_path in exps[domain]:
            exp = loadExperiment(exp_path, Model)

            results = loadResults(exp, 'returns.csv')

            plotBest(results, ax)

        plt.legend()
        save('tests/', 'test', height_ratio=0.75, f=f)
