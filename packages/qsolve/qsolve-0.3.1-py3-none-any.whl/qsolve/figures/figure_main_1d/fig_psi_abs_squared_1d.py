import numpy as np

from numpy import zeros_like

from numpy import pi

from .. style import colors


class fig_psi_abs_squared_1d(object):

    def __init__(self, ax, settings):

        self.hbar = settings.hbar

        # -----------------------------------------------------------------------------------------
        self.line_density, = ax.plot(
            settings.x, zeros_like(settings.x), linewidth=1, linestyle='-',
            color=colors.wet_asphalt, label=r'$\rho$')

        ax.set_xlim(settings.x_min, settings.x_max)
        
        ax.set_ylim(settings.density_min, settings.density_max)

        ax.set_xlabel(settings.label_x)
        
        ax.set_xticks(settings.x_ticks)
        
        ax.grid(visible=True, which='major', color=settings.color_gridlines_major, linestyle='-', linewidth=0.5)
        
        ax.set_ylabel(r'$\mu \mathrm{m}^{-1}$', labelpad=0)
        # -----------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------
        ax2 = ax.twinx()

        self.line_V, = ax2.plot(
            settings.x, zeros_like(settings.x), linewidth=settings.linewidth_V, linestyle='-',
            color=settings.linecolor_V, label=r'$V$')

        ax2.set_xlim(settings.x_min, settings.x_max)
        ax2.set_ylim(settings.V_min, settings.V_max)

        ax2.set_ylabel(r'$h \times \mathrm{kHz}$', labelpad=10)
        # -----------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2,
                   loc='upper right', bbox_to_anchor=(1.0, 1.25), fancybox=True, framealpha=1, ncol=1)
        # -----------------------------------------------------------------------------------------

    def update(self, psi, V):

        density = np.abs(psi)**2

        scaling_V = self.hbar * 2 * pi * 1000

        V = V / scaling_V

        self.line_density.set_ydata(density / 1e6)

        self.line_V.set_ydata(V)
