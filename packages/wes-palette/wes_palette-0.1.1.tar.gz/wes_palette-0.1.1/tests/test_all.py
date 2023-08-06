from matplotlib import rcParams
import matplotlib.pyplot as plt
import cycler
import matplotlib
import numpy as np
import wes_palette as wes


def test_available(show=True):
    wes.available()
    if not show:
        return wes.palettes.keys()
    else:
        f, ax = plt.subplots(5, 2, figsize=(5, 8))
        for i, name in enumerate(wes.palettes.keys()):
            x, y = i // 2, i % 2
            cycle = wes.palettes[name]
            for j, c in enumerate(cycle):
                ax[x, y].hlines(j, 0, 1, colors=c, linewidth=15)
            ax[x, y].set_ylim(-1, len(cycle))
            ax[x, y].set_title(name)
            wes.despine(ax[x, y], True)
        plt.savefig('test.png')
        # plt.show()
    assert wes.available() == plt.show()


test_available()


def test_check_key():
    palettes = {
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
    assert wes.palettes.keys() == palettes.keys()


test_check_key()


def test_cmap():
    palname = 'megasaki'
    assert wes.cmap(palname) == matplotlib.colors.ListedColormap(wes.palettes[palname])


test_cmap()


def test_palette(palname=None):
    assert wes.palette() == wes.palettes

    # print(wes.palette())
    # print(wes.palettes)


test_palette()


def test_reverse():
    assert wes.reverse('megasaki') == list(reversed(wes.palette('megasaki')))


test_reverse()
