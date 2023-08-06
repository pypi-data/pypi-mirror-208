from scipy import constants

import math


class Units1D(object):

    def __init__(self, m_atom):

        # -----------------------------------------------------------------------------------------
        hbar_si = constants.hbar
        mu_B_si = constants.physical_constants['Bohr magneton'][0]
        k_B_si = constants.Boltzmann
        # -----------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------
        unit_mass = m_atom
        unit_length = 1e-6
        unit_time = unit_mass * (unit_length * unit_length) / hbar_si

        unit_electric_current = mu_B_si / (unit_length * unit_length)
        unit_temperature = (unit_mass * unit_length * unit_length) / (k_B_si * unit_time * unit_time)
        # -----------------------------------------------------------------------------------------

        self.unit_length = unit_length

        self.unit_mass = unit_mass

        self.unit_time = unit_time

        self.unit_electric_current = unit_electric_current

        self.unit_temperature = unit_temperature

        self.unit_frequency = 1.0 / unit_time

        self.unit_energy = unit_mass * (unit_length * unit_length) / (unit_time * unit_time)

        self.unit_hbar = (unit_mass * unit_length * unit_length) / unit_time

        self.unit_bohr_magneton = unit_length * unit_length * unit_electric_current

        self.unit_k_B = unit_mass * unit_length * unit_length / (unit_time * unit_time * unit_temperature)

        self.unit_density = 1.0 / unit_length

        self.unit_wave_function = math.sqrt(self.unit_density)
