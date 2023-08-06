#!/usr/bin/env python
from matplotlib import rcParams
import matplotlib.pyplot as plt
import cycler
import matplotlib
import numpy as np


palettes = {
   # "":["#","#"],
    "megasaki":["#aa82a7","#9d2f28","#deb867","#e3ced3","#948580","#110d0e"],
    "budapest":["#4B0100","#900403","#4E1042","#806150","#C76B4F","#D8AA88"],
    "kingdom":["#195B4E","#617337","#B1A16A","#E1D06E","#C99A6B","#B27B7F"],
    "darjeeling":["#0D6CE8","#8ACAF0","#ABBBC7","#687075","#3B5657","#B45E3B"],
    "tenenbaums":["#a7ba42","#95ccba","#ffdede","#fff0cb","#f2cc84"],
    "tracy":["#eaa2b6","#e7cbaf","#e0bd59","#292176"],
    "dispatch":["#1f5c89","#72a87c","#c0bc78","#ce784b"],
    "darjeeling2":["#ffe959","#b5b867","#b7dbdb","#6ba08f","#345b8e"],
    "fantasticfox":["#4baecb","#e4d405","#df8818","#b40c24","#272121"],
    "mendls":["#3a0202","#a03558","#b25d55","#7896d7","#dc90b5","#e0e2f4"],

    #"vaporwave": ["#94D0FF", "#8795E8", "#966bff", "#AD8CFF", "#C774E8", "#c774a9", "#FF6AD5", "#ff6a8b", "#ff8b8b", "#ffa58b", "#ffde8b", "#cdde8b", "#8bde8b", "#20de8b"],
    #"cool": ["#FF6AD5", "#C774E8", "#AD8CFF", "#8795E8", "#94D0FF"],
    #"crystal_pepsi": ["#FFCCFF", "#F1DAFF", "#E3E8FF", "#CCFFFF"],
    #"mallsoft": ["#fbcff3", "#f7c0bb", "#acd0f4", "#8690ff", "#30bfdd", "#7fd4c1"],
    #"jazzcup": ["#392682", "#7a3a9a", "#3f86bc", "#28ada8", "#83dde0"],
    #"sunset": ["#661246", "#ae1357", "#f9247e", "#d7509f", "#f9897b"],
    #"macplus": ["#1b4247", "#09979b", "#75d8d5", "#ffc0cb", "#fe7f9d", "#65323e"],
    #"seapunk": ["#532e57", "#a997ab", "#7ec488", "#569874", "#296656"],
    #"avanti": ["#FB4142", "#94376C", "#CE75AD", "#76BDCF", "#9DCFF0"]
}

# avoid plotly import if not using
plotly_palettes = {k: list(map(list, zip(np.linspace(0, 1, len(palettes[k])), palettes[k]))) for k in palettes}

def available(show=True):
    if not show:
        return palettes.keys()
    else:
        f, ax = plt.subplots(5, 2, figsize=(5, 8))
        for i, name in enumerate(palettes.keys()):
            x, y = i // 2, i % 2
            cycle = palettes[name]
            for j, c in enumerate(cycle):
                ax[x, y].hlines(j, 0, 1, colors=c, linewidth=15)
            ax[x, y].set_ylim(-1, len(cycle))
            ax[x, y].set_title(name)
            despine(ax[x, y], True)
        plt.show()


def check_key(palname):
    try:
        palettes[palname]
    except KeyError:
        raise KeyError("{} not an accepted palette name. Check vapeplot.available() for available palettes".format(palname))


def cmap(palname):
    check_key(palname)
    return matplotlib.colors.ListedColormap(palettes[palname])


def despine(ax, all=False):
    if all is True:
        for sp in ax.spines:
            ax.spines[sp].set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
    else:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()


def font_size(s):
    matplotlib.rcParams.update({'font.size': s})


def palette(palname=None):
    if palname is None:
        return palettes
    else:
        check_key(palname)
        return palettes[palname]


def reverse(palname):
    check_key(palname)
    return list(reversed(palette(palname)))


def set_palette(palname):
        check_key(palname)
        rcParams['axes.prop_cycle'] = cycler.cycler(color=palettes[palname])


def view_palette(*args):
    if len(args) > 1:
        f, ax = plt.subplots(1, len(args), figsize=(3 * len(args), 3))
        for i, name in enumerate(args):
            check_key(name)
            cycle = palettes[name]
            for j, c in enumerate(cycle):
                ax[i].hlines(j, 0, 1, colors=c, linewidth=15)
            ax[i].set_title(name)
            despine(ax[i], True)
        plt.show()
    elif len(args) == 1:
        f = plt.figure(figsize=(3, 3))
        check_key(args[0])
        cycle = palettes[args[0]]
        for j, c in enumerate(cycle):
            plt.hlines(j, 0, 1, colors=c, linewidth=15)
        plt.title(args[0])
        despine(plt.axes(), True)
        f.tight_layout()
        plt.show()
    else:
        raise NotImplementedError("ERROR: supply a palette to plot. check vapeplot.available() for available palettes")
