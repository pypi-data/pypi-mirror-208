from dataclasses import dataclass, field

from scipy import constants

import math


@dataclass(kw_only=True)
class Units:

    unit_length: float = field(default=1.0)
    unit_time: float = field(default=1.0)
    unit_mass: float = field(default=1.0)
    unit_electric_current: float = field(default=1.0)
    unit_temperature: float = field(default=1.0)

    unit_energy: float = field(default=1.0)
    unit_frequency: float = field(default=1.0)

    unit_density: float = field(default=1.0)
    unit_wave_function: float = field(default=1.0)

    unit_hbar: float = field(default=1.0)
    unit_bohr_magneton: float = field(default=1.0)
    unit_k_B: float = field(default=1.0)

    @classmethod
    def solver_units(cls, m_atom: float, dim: int) -> 'Units':

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

        unit_frequency = 1.0 / unit_time

        unit_energy = unit_mass * (unit_length * unit_length) / (unit_time * unit_time)

        unit_hbar = (unit_mass * unit_length * unit_length) / unit_time

        unit_bohr_magneton = unit_length * unit_length * unit_electric_current

        unit_k_B = unit_mass * unit_length * unit_length / (unit_time * unit_time * unit_temperature)

        unit_density = 1.0 / (unit_length**dim)

        unit_wave_function = math.sqrt(unit_density)

        return cls(unit_length=unit_length,
                   unit_time=unit_time,
                   unit_mass=unit_mass,
                   unit_electric_current=unit_electric_current,
                   unit_temperature=unit_temperature,
                   unit_energy=unit_energy,
                   unit_frequency=unit_frequency,
                   unit_density=unit_density,
                   unit_wave_function=unit_wave_function,
                   unit_hbar=unit_hbar,
                   unit_bohr_magneton=unit_bohr_magneton,
                   unit_k_B=unit_k_B
                   )
