from qsolve.solvers.solvers_3d.solver_gpe_3d.units import Units

from scipy import constants


def init_units(self, kwargs):

    # ---------------------------------------------------------------------------------------------
    hbar_si = constants.hbar
    mu_B_si = constants.physical_constants['Bohr magneton'][0]
    k_B_si = constants.Boltzmann
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    unit_mass = kwargs['m_atom']
    unit_length = 1e-6
    unit_time = unit_mass * (unit_length * unit_length) / hbar_si

    unit_electric_current = mu_B_si / (unit_length * unit_length)
    unit_temperature = (unit_mass * unit_length * unit_length) / (k_B_si * unit_time * unit_time)
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    self.units = Units(unit_length, unit_time, unit_mass, unit_electric_current, unit_temperature)
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    self.hbar = hbar_si / self.units.unit_hbar
    self.mu_B = mu_B_si / self.units.unit_bohr_magneton
    self.k_B = k_B_si / self.units.unit_k_B

    self.m_atom = kwargs['m_atom'] / self.units.unit_mass
    self.a_s = kwargs['a_s'] / self.units.unit_length
    self.g = 4.0 * constants.pi * self.hbar ** 2 * self.a_s / self.m_atom

    assert (self.hbar == 1.0)
    assert (self.mu_B == 1.0)
    assert (self.k_B == 1.0)

    assert (self.m_atom == 1.0)
    # ---------------------------------------------------------------------------------------------
