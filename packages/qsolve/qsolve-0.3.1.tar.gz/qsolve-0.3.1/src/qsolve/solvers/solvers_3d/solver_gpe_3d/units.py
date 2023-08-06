from math import sqrt


class Units(object):

    def __init__(self, unit_length, unit_time, unit_mass, unit_electric_current, unit_temperature):

        self.unit_length = unit_length

        self.unit_mass = unit_mass

        self.unit_time = unit_time

        self.unit_electric_current = unit_electric_current

        self.unit_temperature = unit_temperature

        self.unit_frequency = 1.0 / unit_time

        self.unit_energy = unit_mass * (unit_length * unit_length) / (unit_time * unit_time)

        self.unit_wave_function = 1.0 / sqrt(unit_length * unit_length * unit_length)

        self.unit_density = 1.0 / (unit_length * unit_length * unit_length)

        self.unit_hbar = (unit_mass * unit_length * unit_length) / unit_time

        self.unit_bohr_magneton = unit_length * unit_length * unit_electric_current

        self.unit_k_B = unit_mass * unit_length * unit_length / (unit_time * unit_time * unit_temperature)

        self.unit_g = unit_mass * (unit_length * unit_length * unit_length
                                   * unit_length * unit_length) / (unit_time * unit_time)
