import matplotlib as mpl
import matplotlib.pyplot as plt


def init_mpl_settings(usetex=False):

    if usetex:

        mpl.use("pgf")

        str_pgf_preamble = \
            "\\usepackage{amsmath}\n" \
            "\\usepackage{amsfonts}\n" \
            "\\usepackage{amssymb}\n" \
            "\\usepackage{bbm}\n" \
            "\\usepackage{bm}\n" \
            "\\usepackage{icomma}"

        mpl.rcParams["pgf.preamble"] = str_pgf_preamble

        mpl.rcParams["text.usetex"] = True

        mpl.rcParams['font.family'] = 'sans-serif'

        mpl.rcParams['pgf.rcfonts'] = True

        mpl.rcParams['font.size'] = 14

        mpl.rcParams['axes.titlesize'] = 14
        mpl.rcParams['axes.labelsize'] = 14

        mpl.rcParams['xtick.labelsize'] = 14
        mpl.rcParams['ytick.labelsize'] = 14

        mpl.rcParams['legend.fontsize'] = 14

        mpl.rcParams['figure.titlesize'] = 14

    else:

        plt.rcParams['font.family'] = "sans-serif"

        plt.rcParams['font.size'] = 11

        mpl.rcParams['axes.titlesize'] = 11
        mpl.rcParams['axes.labelsize'] = 11

        mpl.rcParams['xtick.labelsize'] = 11
        mpl.rcParams['ytick.labelsize'] = 11

        mpl.rcParams['legend.fontsize'] = 11

        mpl.rcParams['figure.titlesize'] = 11
