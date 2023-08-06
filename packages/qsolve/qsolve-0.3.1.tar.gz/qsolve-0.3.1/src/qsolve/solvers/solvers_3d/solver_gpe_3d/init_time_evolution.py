import numpy as np


def init_time_evolution(self, kwargs):

    self.t_final = kwargs["t_final"] / self.units.unit_time
    self.dt = kwargs["dt"] / self.units.unit_time

    self.n_time_steps = int(np.round(self.t_final / self.dt))

    self.n_times = self.n_time_steps + 1

    assert (np.abs(self.n_time_steps * self.dt - self.t_final)) < 1e-14

    self.times = self.dt * np.arange(self.n_times)

    assert (np.abs(self.times[-1] - self.t_final)) < 1e-14
