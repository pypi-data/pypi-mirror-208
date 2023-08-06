from qsolve.core import qsolve_core_gpe_3d


def compute_density_xy(self, identifier, kwargs):

    if "rescaling" in kwargs:

        rescaling = kwargs["rescaling"]

    else:

        rescaling = False

    if identifier == "psi_tof_gpe":

        if "index_z" in kwargs:

            index_z = kwargs["index_z"]

        else:

            index_z = self.index_center_z_tof_free_gpe

        density_xy = qsolve_core_gpe_3d.compute_density_xy(self.psi_tof_free_gpe, index_z, rescaling)

    elif identifier == "psi_f_tof_free_schroedinger":

        if "index_z" in kwargs:

            index_z = kwargs["index_z"]

        else:

            index_z = self.index_center_z_f_tof_free_schroedinger

        density_xy = qsolve_core_gpe_3d.compute_density_xy(self.psi_f_tof_free_schroedinger, index_z, rescaling)

    else:

        message = 'compute_density_xz(identifier, **kwargs): identifier \'{0:s}\' not supported'.format(identifier)

        raise Exception(message)

    return density_xy.cpu().numpy()


def compute_density_xz(self, identifier, kwargs):

    if "rescaling" in kwargs:

        rescaling = kwargs["rescaling"]

    else:

        rescaling = False

    if identifier == "psi_tof_gpe":

        if "index_y" in kwargs:

            index_y = kwargs["index_y"]

        else:

            index_y = self.index_center_y_tof_free_gpe

        density_xz = qsolve_core_gpe_3d.compute_density_xz(self.psi_tof_free_gpe, index_y, rescaling)

    elif identifier == "psi_f_tof_free_schroedinger":

        if "index_y" in kwargs:

            index_y = kwargs["index_y"]

        else:

            index_y = self.index_center_y_f_tof_free_schroedinger

        density_xz = qsolve_core_gpe_3d.compute_density_xz(self.psi_f_tof_free_schroedinger, index_y, rescaling)

    else:

        message = 'compute_density_xz(identifier, **kwargs): identifier \'{0:s}\' not supported'.format(identifier)

        raise Exception(message)

    return density_xz.cpu().numpy()
