import numpy as np
from typing import Any, Callable, Dict, List, Optional
from PyExpUtils.results.backends.backend import DuckResult, ResultList
from PyExpUtils.results.results import splitOverParameter, getBest
from scipy.stats.kde import gaussian_kde
import PyExpUtils.utils.dict as DictUtils

# TODO: split this into 2 dictionaries. One that contains user-specified options
# and another that contains context information (e.g. best params for an algorithm)
# also, when we make the split, organize the options into a meaningful order somehow

# TODO: see if we can use python 3.8+ and use typed-dicts instead, that way we can
# start type-checking this library
def buildOptions(options: Optional[Dict[str, Any]]):
    options = options if options is not None else {}
    out_options = {}

    out_options['prefer'] = options.get('prefer', 'big')
    out_options['y_offset'] = options.get('y_offset', 0)
    out_options['spacing'] = options.get('spacing', 1.0)
    out_options['alg_spacing'] = options.get('alg_spacing', 0.75)
    out_options['x_range'] = options.get('x_range')
    out_options['color'] = options.get('color')
    out_options['colors'] = options.get('colors', {})
    out_options['label'] = options.get('label')
    out_options['bins'] = options.get('bins', 30)
    out_options['alpha'] = options.get('alpha', 0.6)
    out_options['fidelity'] = options.get('fidelity', 200)
    out_options['kde'] = options.get('kde', True)
    out_options['hist'] = options.get('hist', True)
    out_options['dist_height'] = options.get('dist_height', 0.9)
    out_options['y_ticks'] = options.get('y_ticks', True)
    out_options['process_y_ticks'] = options.get('process_y_ticks', lambda x: x)
    out_options['highlight_top'] = options.get('highlight_top', False)
    out_options['highlight_level'] = options.get('highlight_level', 0.2)
    out_options['highlight'] = options.get('highlight', True)
    out_options['best_params'] = options.get('best_params')  # <-- actually a context variable
    out_options['best_param'] = options.get('best_param')  # <-- also context, and worse only useful for some of the funcs but not all

    return out_options

def minMaxScale(x):
    return (x - np.min(x)) / (np.max(x) - np.min(x))

def pullLeft(x, p):
    if x < 0:
        return (1 + p) * x

    return (1 - p) * x

def pullRight(x, p):
    return -pullLeft(-x, p)

def plot(result: DuckResult, ax, reducer: Callable[[np.ndarray], float], options: Optional[Dict[str, Any]] = None):
    o = buildOptions(options)

    if not o['hist'] and not o['kde']:
        raise Exception("Well if you don't want a histogram or kde, then what *do* you want??")

    curves = result.load()
    points = [reducer(curve) for curve in curves]

    if o['x_range'] is None:
        lo = np.min(points)
        hi = np.max(points)

    else:
        lo, hi = o['x_range']

    lo = pullLeft(lo, 0.02)
    hi = pullRight(hi, 0.02)

    alpha = 1
    if not o['highlight']:
        alpha = o['highlight_level']

    if o['hist']:
        bins = o['bins']
        hist, _ = np.histogram(points, bins=bins, range=(lo, hi))
        hist = minMaxScale(hist) * o['dist_height']
        hist_x = np.linspace(lo, hi, bins)

        ax.bar(hist_x, hist, bottom=o['y_offset'], width=(hi - lo) / bins, color=o['color'], alpha=o['alpha'] * alpha)

    if o['kde']:
        kde = gaussian_kde(points)
        dist_space = np.linspace(lo, hi, o['fidelity'])
        dist = minMaxScale(kde(dist_space)) * o['dist_height'] + o['y_offset']
        ax.plot(dist_space, dist, linewidth=1.0, color=o['color'], alpha=alpha)

        # if we only want a KDE, then shade in the region under the curve
        if not o['hist']:
            ax.fill_between(dist_space, np.zeros(o['fidelity']) + o['y_offset'], dist, color=o['color'], alpha=0.2 * alpha)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

def stacked(result_dict: Dict[Any, DuckResult], ax, reducer: Callable[[np.ndarray], float], options: Optional[Dict[str, Any]] = None):
    o = buildOptions(options)

    y_ticks = []
    y_offset = o['y_offset']
    for key in result_dict:
        o['y_offset'] = y_offset

        if o['highlight_top'] and o['best_param'] == key:
            o['highlight'] = True
        elif o['highlight_top']:
            o['highlight'] = False

        plot(result_dict[key], ax, reducer, o)

        y_ticks.append(y_offset)
        y_offset += o['spacing']

    empty_ticks = all([tick.get_text() == '' for tick in ax.get_yticklabels()])
    if empty_ticks and o['y_ticks']:
        y_labels = list(result_dict)
        ax.yaxis.set_ticks(y_ticks)
        y_labels = list(map(o['process_y_ticks'], y_labels))
        ax.set_yticklabels(y_labels)

def stackedAlgs(result_dicts: List[Dict[Any, DuckResult]], ax, reducer: Callable[[np.ndarray], float], options: Optional[Dict[str, Any]] = None):
    o = buildOptions(options)

    lo = np.inf
    hi = -np.inf

    for alg_dict in result_dicts:
        for key in alg_dict:
            curves = alg_dict[key].load()
            points = [reducer(curve) for curve in curves]

            lo = np.min(points + [lo])
            hi = np.max(points + [hi])

    o['x_range'] = (lo, hi)
    y_offset = 0
    center_alg = int(len(result_dicts) // 2)
    for idx, alg_dict in enumerate(result_dicts):
        o['y_offset'] = y_offset
        o['y_ticks'] = idx == center_alg

        key = list(alg_dict)[0]

        if hasattr(alg_dict[key].exp, 'agent'):
            alg = alg_dict[key].exp.agent
            o['color'] = o['colors'].get(alg)

        if o['best_params']:
            o['best_param'] = o['best_params'][idx]

        stacked(alg_dict, ax, reducer, o)

        y_offset += o['alg_spacing']

def parameterStudyAlgs(
        results: List[ResultList],
        ax,
        param: str,
        reducer: Callable[[np.ndarray], float],
        options: Optional[Dict[str, Any]] = None,
    ):
    o = buildOptions(options)

    # account for the fact that there are multiple algorithms
    o['spacing'] = len(results) * o['alg_spacing'] + o['spacing']

    alg_dicts = []
    best_params = []
    for alg_results in results:
        alg_results = list(alg_results)
        total_best = getBest(alg_results, prefer=o['prefer'])
        best_params.append(DictUtils.get(total_best.params, param))

        param_dict = splitOverParameter(alg_results, param)

        result_dict = {}
        for key in param_dict:
            result_dict[key] = getBest(param_dict[key], prefer=o['prefer'])

        alg_dicts.append(result_dict)

    o['best_params'] = best_params
    stackedAlgs(alg_dicts, ax, reducer, o)
