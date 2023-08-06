from qsolve.core import qsolve_core_gpe_3d


def compute_n_atoms(self, identifier):

    if identifier == "psi":

        n_atoms = qsolve_core_gpe_3d.compute_n_atoms(self.psi, self.dx, self.dy, self.dz)

    elif identifier == "psi_0":

        n_atoms = qsolve_core_gpe_3d.compute_n_atoms(self.psi_0, self.dx, self.dy, self.dz)

    else:

        message = 'identifier \'{0:s}\' not supported for this operation'.format(identifier)

        raise Exception(message)

    return n_atoms
