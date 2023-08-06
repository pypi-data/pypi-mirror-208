# wes_palette/wes_palette.py

"""Provide several color palettes for matplotlib.
This module allows the user to easily change default color palettes in matplotlib.

This module contains the followinng functions:

- 'available(show=True)' - Returns a visual of all available color palettes.
- 'check_key(palname)' - Check if palette name is in available palettes
- 'cmap(palname)' - Return matplotlib color map of palette
- 'despine(ax, all=False)' - Removes axis labels from graph
- 'font_size(s)' - Set font size
- 'palette(palname=None)' - Return all palettes if no palname; otherwise check and return palname from palette
- 'reverse(palname)' -  Reverse color order
- 'set_palette(palname)' - Set palette
- 'view_palette(*args)' - View color palette

"""

#!/usr/bin/env python
from matplotlib import rcParams
import matplotlib.pyplot as plt
import cycler
import matplotlib
import numpy as np


palettes = {
    #"": ["", ""],
    "megasaki": ["#aa82a7", "#9d2f28", "#deb867", "#e3ced3", "#948580", "#110d0e"],
    "budapest": ["#4B0100", "#900403", "#4E1042", "#806150", "#C76B4F", "#D8AA88"],
    "kingdom": ["#195B4E", "#617337", "#B1A16A", "#E1D06E", "#C99A6B", "#B27B7F"],
    "darjeeling": ["#0D6CE8", "#8ACAF0", "#ABBBC7", "#687075", "#3B5657", "#B45E3B"],
    "tenenbaums": ["#a7ba42", "#95ccba", "#ffdede", "#fff0cb", "#f2cc84"],
    "tracy": ["#eaa2b6", "#e7cbaf", "#e0bd59", "#292176"],
    "dispatch": ["#1f5c89", "#72a87c", "#c0bc78", "#ce784b"],
    "darjeeling2": ["#ffe959", "#b5b867", "#b7dbdb", "#6ba08f", "#345b8e"],
    "fantasticfox": ["#4baecb", "#e4d405", "#df8818", "#b40c24", "#272121"],
    "mendls": ["#3a0202", "#a03558", "#b25d55", "#7896d7", "#dc90b5", "#e0e2f4"],
}

# avoid plotly import if not using
plotly_palettes = {k: list(map(list, zip(np.linspace(0, 1, len(palettes[k])), palettes[k]))) for k in palettes}


def available(show=True):
    """Output graphs of all available color palettes."""
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
    """Check if palette is in palette list.
	#Args:
	#	palname: palette name
	#Returns:
	#	Tries color palette or raises error
	Raises:
		KeyError: An error occurs when the palette name is new.
	Examples:
		>>> check_key("megasaki")
		
    """

    try:
        palettes[palname]
    except KeyError:
        raise KeyError(
            "{} not an accepted palette name. Check vapeplot.available() for available palettes".format(palname)
        )


def cmap(palname):
    """Check if palette is vaild and make a colormap from it.
	#Args:
	#	palname: palette name 
	#Returns:
	#	matplotlib colormap
	Examples:
		#>>> cmap("megasaki")
		#<matplotlib.colors.ListedColormap object at > 
    """

    check_key(palname)
    return matplotlib.colors.ListedColormap(palettes[palname])


def despine(ax, all=False):
    """Remove axis labels from graph.
	Examples:
		#>>> despine(ax, True)

    """
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
    """Set font size.i
	Examples:
		>>> font_size(11)
		
    """
    matplotlib.rcParams.update({'font.size': s})


def palette(palname=None):
    """If no argument, return list of palettes. 
       Otherwise check the palette name and return the palette.
	Examples:
		>>> palette()
		{'megasaki': ['#aa82a7', '#9d2f28', '#deb867', '#e3ced3', '#948580', '#110d0e'], 'budapest': ['#4B0100', '#900403', '#4E1042', '#806150', '#C76B4F', '#D8AA88'], 'kingdom': ['#195B4E', '#617337', '#B1A16A', '#E1D06E', '#C99A6B', '#B27B7F'], 'darjeeling': ['#0D6CE8', '#8ACAF0', '#ABBBC7', '#687075', '#3B5657', '#B45E3B'], 'tenenbaums': ['#a7ba42', '#95ccba', '#ffdede', '#fff0cb', '#f2cc84'], 'tracy': ['#eaa2b6', '#e7cbaf', '#e0bd59', '#292176'], 'dispatch': ['#1f5c89', '#72a87c', '#c0bc78', '#ce784b'], 'darjeeling2': ['#ffe959', '#b5b867', '#b7dbdb', '#6ba08f', '#345b8e'], 'fantasticfox': ['#4baecb', '#e4d405', '#df8818', '#b40c24', '#272121'], 'mendls': ['#3a0202', '#a03558', '#b25d55', '#7896d7', '#dc90b5', '#e0e2f4']}
    """
    if palname is None:
        return palettes
    else:
        check_key(palname)
        return palettes[palname]


def reverse(palname):
    """Reverse color order of specfied palette.
	Examples:
		#>>> reverse("budapest")
		#['#D8AA88', '#C76B4F', '#806150', '#4E1042', '#900403', '#4B0100']	
    """
    check_key(palname)
    return list(reversed(palette(palname)))


def set_palette(palname):
    """Check the palette name and set the palette
	Examples:
		>>> set_palette("budapest")
		
    """
    check_key(palname)
    rcParams['axes.prop_cycle'] = cycler.cycler(color=palettes[palname])


def view_palette(*args):
    """Display the palette.
	Raises:
		NotImplementedError: An error occurs when palette not specified or not valid.	
	Examples:
		>>> view_palette("budapest")
    """
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
        raise NotImplementedError("ERROR: supply a palette to plot. check wes_palette.available() for available palettes")
