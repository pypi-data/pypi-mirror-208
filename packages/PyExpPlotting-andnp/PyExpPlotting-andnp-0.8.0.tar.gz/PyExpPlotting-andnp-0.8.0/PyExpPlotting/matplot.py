from typing import Optional, Union
import os
import importlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyExpPlotting.defaults import ICML_Dimensions, PaperDimensions, getDefaultDimensions

default_conference = ICML_Dimensions
def setDefaultConference(conference: Union[str, PaperDimensions]):
    global default_conference
    if type(conference) is str:
        default_conference = getDefaultDimensions(conference)

    elif type(conference) is PaperDimensions:
        default_conference = conference

    else:
        raise NotImplementedError('Should be unreachable, but types say otherwise')

    setFonts(default_conference.font_size)

def setFonts(font_size: int):
    small = font_size - 4
    medium = font_size - 2
    large = font_size

    plt.rc('font', size=small)          # controls default text sizes
    plt.rc('axes', titlesize=medium)    # fontsize of the axes title
    plt.rc('axes', labelsize=medium)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=small)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=small)    # fontsize of the tick labels
    plt.rc('legend', fontsize=medium)   # legend fontsize
    plt.rc('figure', titlesize=large)   # fontsize of the figure title

def save(
        save_path: str,
        plot_name: str,
        plot_type: Optional[str] = None,
        dims: Optional[PaperDimensions] = None,
        save_type: str = 'png',
        width: float = 1.0,
        height_ratio: float = 1.0,
        f: Optional[Figure] = None,
    ):

    # don't make this a default because it could be changed
    # after this function is parsed
    if f is None:
        f = plt.gcf()

    # likewise could be changed after function parse
    # so cannot be a default parameter
    if not dims:
        dims = default_conference

    # too much logic to stick in default parameters
    if plot_type is None:
        main_file = importlib.import_module('__main__').__file__
        assert main_file is not None
        plot_type = os.path.basename(main_file).replace('.py', '').replace('_', '-')

    save_path = f'{save_path}/{plot_type}'
    os.makedirs(save_path, exist_ok=True)

    width = width * dims.column_width
    height = width * height_ratio
    f.set_size_inches((width, height), forward=True)
    f.savefig(f'{save_path}/{plot_name}.{save_type}', dpi=600, bbox_inches='tight')
