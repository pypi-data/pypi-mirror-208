import torch


def eval_potential_gaussian_3d(x_3d, y_3d, z_3d, sigma_x, sigma_y, sigma_z):

    V_x = torch.exp(-(x_3d**2) / (2 * sigma_x**2))
    V_y = torch.exp(-(y_3d**2) / (2 * sigma_y**2))
    V_z = torch.exp(-(z_3d**2) / (2 * sigma_z**2))

    V = V_x * V_y * V_z

    return V
