import torch

from numpy import pi


def eval_potential_lattice_z_3d(z_3d, Lz, m):

    V_z = 0.5 * (torch.cos(2.0 * pi * m * z_3d / Lz) + 1.0)

    return V_z
