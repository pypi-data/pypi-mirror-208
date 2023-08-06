import torch


def eval_potential_gaussian_2d(x_2d, y_2d, sigma_x, sigma_y):

    V_x = torch.exp(-(x_2d**2) / (2 * sigma_x**2))
    V_y = torch.exp(-(y_2d**2) / (2 * sigma_y**2))

    V = V_x * V_y

    return V
