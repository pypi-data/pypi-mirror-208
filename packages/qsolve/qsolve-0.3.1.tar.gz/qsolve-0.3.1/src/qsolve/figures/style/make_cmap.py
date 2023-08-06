import sys

import matplotlib as mpl
import numpy as np


def make_cmap(colors, positions=None, bit=False):
    """
    make_cmap takes a list of tuples which contain RGB values. The RGB
    values may either be in 8-bit [0 to 255] (in which bit must be set to
    True when called) or arithmetic [0 to 1] (default). make_cmap returns
    a cmap with equally spaced colors.
    Arrange your tuples so that the first color is the lowest value for the
    colorbar and the last is the highest.
    position contains values from 0 to 1 to dictate the location of each color.
    """

    bit_rgb = np.linspace(0.0, 1.0, 256)

    if positions is None:

        positions = np.linspace(0.0, 1.0, len(colors))

    else:

        if len(positions) != len(colors):

            sys.exit("position length must be the same as colors")

        elif positions[0] != 0 or positions[-1] != 1:

            sys.exit("position must start with 0 and end with 1")

    if bit:

        for i in range(len(colors)):

            colors[i] = (bit_rgb[colors[i][0]],
                         bit_rgb[colors[i][1]],
                         bit_rgb[colors[i][2]])

    cdict = {'red': [], 'green': [], 'blue': []}

    for pos, color in zip(positions, colors):

        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = mpl.colors.LinearSegmentedColormap('my_colormap', cdict, 256)

    return cmap
