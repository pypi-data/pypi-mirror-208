import numpy as np
from dataclasses import dataclass
from matplotlib.axes import Axes

from PyExpPlotting.colors import ColorPalette

@dataclass
class LineplotOptions:
    label: str | None = None
    color: ColorPalette = ColorPalette()

    linewidth: float = 0.25
    alpha: float = 0.2

    legend: bool = True
    x_label: str | None = None
    y_label: str | None = None
    title: str | None = None

def plotLearningCurve(data: np.ndarray, ax: Axes, lo: np.ndarray | None = None, hi: np.ndarray | None = None, options: LineplotOptions = LineplotOptions()):
    color = options.color.get(options.label)
    ax.plot(data, label=options.label, color=color, linewidth=options.linewidth)

    if lo is not None and hi is not None:
        ax.fill_between(range(data.shape[0]), lo, hi, color=color, alpha=options.alpha)

    # TODO: make this a shared method
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    if options.legend:
        ax.legend(frameon=False)

    if options.x_label is not None:
        ax.set_xlabel(options.x_label)

    if options.y_label is not None:
        ax.set_ylabel(options.y_label)

    if options.title is not None:
        ax.set_title(options.title)

@dataclass
class AllLinesPlotOptions(LineplotOptions):
    summary: str | None = 'mean'
    max_lines: int = 30

def plotAllLearningCurves(data: np.ndarray, ax: Axes, options: AllLinesPlotOptions = AllLinesPlotOptions()):
    color = options.color.get(options.label)

    assert data.ndim == 2
    idxs = np.arange(data.shape[0])
    if options.max_lines < data.shape[0]:
        top = int(options.max_lines / 2)
        bottom = options.max_lines - top

        scores = np.mean(data, axis=1)
        sorted_idxs = np.argsort(scores)
        bottom_idxs = sorted_idxs[:bottom]
        top_idxs = sorted_idxs[-top:]

        idxs = np.concatenate((bottom_idxs, top_idxs))

    label = options.label
    for idx in idxs:
        ax.plot(data[idx], label=label, color=color, linewidth=options.linewidth, alpha=options.alpha)
        label = None

    if options.summary == 'mean':
        mean = np.mean(data, axis=0)
        ax.plot(mean, color=color, linewidth=options.linewidth)

    # TODO: make this a shared method
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    if options.legend:
        ax.legend(frameon=False)

    if options.x_label is not None:
        ax.set_xlabel(options.x_label)

    if options.y_label is not None:
        ax.set_ylabel(options.y_label)

    if options.title is not None:
        ax.set_title(options.title)
