import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from anutils.utils import flatten


def plot_learning_curve(data: pd.DataFrame,
                        keys: list,
                        suptitle='',
                        save: str = None,
                        style: str = 'default'):
    r"""
    data: dict of curves
    keys: list specifying the plot structures. E.g., [['tl', 'vl], ['ta', 'va']] means two subplots. 
    """
    plt.style.use(style)
    plt.rc('font', family='Helvetica')
    plt.rcParams['pdf.fonttype'] = 42

    n_subplots = len(keys)
    w = np.ceil(np.sqrt(n_subplots)).astype(int)
    h = np.ceil(n_subplots / w).astype(int)
    plt.figure(figsize=[5 * w, 5 * h], dpi=80, facecolor='white')
    for i_subp in range(n_subplots):
        plt.subplot(h, w, i_subp + 1)
        sns.lineplot(data=data.loc[:, keys[i_subp]], dashes=False)
        plt.grid()
    plt.suptitle(suptitle)
    if save:
        plt.savefig(save)
        plt.close()
    else:
        plt.show()


def get_learning_curve_from_txt(
    path: str,
    keys: list = None,
    plot: str = None,
    plot_structure: list = None,
    suptitle: str = 'learning_curve',
    format: str = 'png',
    style: str = 'default',
) -> pd.DataFrame:
    r"""
    keys: a tuple of keys to collect. If None, infer from plot_structure. 
    plot: path to save fig
    plot_structure: see plot_learning_curve
    format: `png` or `pdf`
    """
    if keys is None:
        keys = flatten(plot_structure)
    out = dict()
    for key in keys:
        out[key] = []

    try:
        with open(path, 'r') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(path, 'r', encoding='utf16') as f:
            lines = f.readlines()
    for line in lines:
        line = (line.replace(",", " ").replace(":", " ").replace("=", " "))
        words = line.split()
        words = [word.strip('`\'\"()[]{}') for word in words]
        for key in keys:
            if key in words:
                value = float(words[words.index(key) + 1])
                out[key].append(value)
    out = pd.DataFrame(out)
    if plot:
        if isinstance(plot, bool):
            assert (path.endswith(".txt"))
            plot = path[:-4] + '_learning_curve.' + format
        elif not isinstance(plot, str):
            raise (AttributeError)
        plot_learning_curve(out, keys=plot_structure, suptitle=suptitle, save=plot, style=style)
    return out
