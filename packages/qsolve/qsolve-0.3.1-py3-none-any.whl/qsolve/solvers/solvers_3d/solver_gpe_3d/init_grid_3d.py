import torch

import numpy as np

from qsolve.primes import get_prime_factors


def init_grid(self, kwargs):

    self.x_min = kwargs['x_min'] / self.units.unit_length
    self.x_max = kwargs['x_max'] / self.units.unit_length

    self.y_min = kwargs['y_min'] / self.units.unit_length
    self.y_max = kwargs['y_max'] / self.units.unit_length

    self.z_min = kwargs['z_min'] / self.units.unit_length
    self.z_max = kwargs['z_max'] / self.units.unit_length

    self.Jx = kwargs['Jx']
    self.Jy = kwargs['Jy']
    self.Jz = kwargs['Jz']

    prime_factors_Jx = get_prime_factors(self.Jx)
    prime_factors_Jy = get_prime_factors(self.Jy)
    prime_factors_Jz = get_prime_factors(self.Jz)

    assert (np.max(prime_factors_Jx) < 11)
    assert (np.max(prime_factors_Jy) < 11)
    assert (np.max(prime_factors_Jz) < 11)

    assert (self.Jx % 2 == 0)
    assert (self.Jy % 2 == 0)
    assert (self.Jz % 2 == 0)

    x = np.linspace(self.x_min, self.x_max, self.Jx, endpoint=False)
    y = np.linspace(self.y_min, self.y_max, self.Jy, endpoint=False)
    z = np.linspace(self.z_min, self.z_max, self.Jz, endpoint=False)

    self.index_center_x = np.argmin(np.abs(x))
    self.index_center_y = np.argmin(np.abs(y))
    self.index_center_z = np.argmin(np.abs(z))

    assert (np.abs(x[self.index_center_x]) < 1e-14)
    assert (np.abs(y[self.index_center_y]) < 1e-14)
    assert (np.abs(z[self.index_center_z]) < 1e-14)

    self.dx = x[1] - x[0]
    self.dy = y[1] - y[0]
    self.dz = z[1] - z[0]

    self.Lx = self.Jx * self.dx
    self.Ly = self.Jy * self.dy
    self.Lz = self.Jz * self.dz

    self.x = torch.tensor(x, dtype=torch.float64, device=self.device)
    self.y = torch.tensor(y, dtype=torch.float64, device=self.device)
    self.z = torch.tensor(z, dtype=torch.float64, device=self.device)

    self.x_3d = torch.reshape(self.x, (self.Jx, 1, 1))
    self.y_3d = torch.reshape(self.y, (1, self.Jy, 1))
    self.z_3d = torch.reshape(self.z, (1, 1, self.Jz))
