from qsolve.core import qsolve_core_gpe_3d


def compute_chemical_potential(self, identifier, kwargs):

    if "units" in kwargs:

        units = kwargs["units"]

    else:

        units = "si_units"

    if identifier == "psi":

        mue = qsolve_core_gpe_3d.compute_chemical_potential(
            self.psi,
            self.V,
            self.dx,
            self.dy,
            self.dz,
            self.hbar,
            self.m_atom,
            self.g)

    elif identifier == "psi_0":

        mue = qsolve_core_gpe_3d.compute_chemical_potential(
            self.psi_0,
            self.V,
            self.dx,
            self.dy,
            self.dz,
            self.hbar,
            self.m_atom,
            self.g)

    else:

        message = 'compute_chemical_potential(self, identifier, **kwargs): ' \
                  'identifier \'{0:s}\'not supported'.format(identifier)

        raise Exception(message)

    if units == "si_units":

        return self.units.unit_energy * mue

    else:

        return mue
