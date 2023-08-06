import torch


def eval_potential_gaussian_z_3d(z_3d, sigma_z):

    V = torch.exp(-z_3d**2 / (2 * sigma_z**2))

    return V
