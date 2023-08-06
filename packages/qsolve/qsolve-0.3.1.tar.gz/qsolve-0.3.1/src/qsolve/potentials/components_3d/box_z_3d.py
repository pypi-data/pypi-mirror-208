import torch


def eval_potential_box_z_3d(z_3d, z1, z2, s):

    V1 = 1.0 / (1.0 + torch.exp(-(z_3d - z1) / s))
    V2 = 1.0 / (1.0 + torch.exp((z_3d - z2) / s))

    V = V1 + V2

    return V
