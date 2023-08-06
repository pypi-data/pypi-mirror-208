from qsolve.core import qsolve_core_gpe_3d


def compute_spectrum_abs_xy(self, identifier, kwargs):

    if "rescaling" in kwargs:

        rescaling = kwargs["rescaling"]

    else:

        rescaling = False

    if identifier == "psi_tof_gpe":

        if "index_z" in kwargs:

            index_z = kwargs["index_z"]

        else:

            index_z = self.index_center_z_tof_free_gpe

        spectrum_abs_xy = qsolve_core_gpe_3d.compute_spectrum_abs_xy(self.psi_tof_free_gpe, index_z, rescaling)

    else:

        message = 'compute_spectrum_abs_xy(self, identifier, **kwargs): \'identifier \'{0:s}\' ' \
                  'not supported'.format(identifier)

        raise Exception(message)

    spectrum_abs_xy = spectrum_abs_xy.cpu().numpy()

    return spectrum_abs_xy


def compute_spectrum_abs_xz(self, identifier, kwargs):

    if "rescaling" in kwargs:

        rescaling = kwargs["rescaling"]

    else:

        rescaling = False

    if identifier == "psi_tof_gpe":

        if "index_y" in kwargs:

            index_y = kwargs["index_y"]

        else:

            index_y = self.index_center_y_tof_free_gpe

        spectrum_abs_xz = qsolve_core_gpe_3d.compute_spectrum_abs_xz(self.psi_tof_free_gpe, index_y, rescaling)

    else:

        message = 'compute_spectrum_abs_xy(self, identifier, **kwargs): \'identifier \'{0:s}\' ' \
                  'not supported'.format(identifier)

        raise Exception(message)

    spectrum_abs_xz = spectrum_abs_xz.cpu().numpy()

    return spectrum_abs_xz
