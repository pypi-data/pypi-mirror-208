import torch

import scipy

import numpy as np

import sys

import math

from qsolve.core import qsolve_core_gpe_1d

from qsolve.primes import get_prime_factors

from qsolve.units import Units


class SolverGPE1D(object):

    def __init__(self, *, m_atom, a_s, omega_perp, seed=0, device='cpu', num_threads_cpu=1):

        # -----------------------------------------------------------------------------------------
        print("Python version:")
        print(sys.version)
        print()
        print("PyTorch version:")
        print(torch.__version__)
        print()
        # -----------------------------------------------------------------------------------------

        torch.manual_seed(seed)

        torch.set_num_threads(num_threads_cpu)

        self._device = torch.device(device)

        self._units = Units.solver_units(m_atom, dim=1)

        # -----------------------------------------------------------------------------------------
        self._hbar = scipy.constants.hbar / self._units.unit_hbar
        self._mu_B = scipy.constants.physical_constants['Bohr magneton'][0] / self._units.unit_bohr_magneton
        self._k_B = scipy.constants.Boltzmann / self._units.unit_k_B

        self._m_atom = m_atom / self._units.unit_mass
        self._a_s = a_s / self._units.unit_length

        _omega_perp = omega_perp / self._units.unit_frequency

        _g_3d = 4.0 * scipy.constants.pi * self._hbar ** 2 * self._a_s / self._m_atom

        _a_perp = math.sqrt(self._hbar / (self._m_atom * _omega_perp))

        self._g = _g_3d / (2 * math.pi * _a_perp**2)

        assert (self._hbar == 1.0)
        assert (self._mu_B == 1.0)
        assert (self._k_B == 1.0)

        assert (self._m_atom == 1.0)
        # -----------------------------------------------------------------------------------------

        self._x = None

        self._x_min = None
        self._x_max = None

        self._Lx = None

        self._Jx = None
        self._dx = None

        self._compute_external_potential = None
        self._V = None

        self._psi = None

        self._t_final = None
        self._dt = None
        self._n_time_steps = None
        self._n_times = None
        self._times = None
        self._t = 0.0

        self._p = {
            "hbar": self._hbar,
            "mu_B": self._mu_B,
            "k_B": self._k_B,
            "m_atom": self._m_atom
        }

    def init_grid(self, **kwargs):

        self._x_min = kwargs['x_min'] / self._units.unit_length
        self._x_max = kwargs['x_max'] / self._units.unit_length

        self._Jx = kwargs['Jx']

        assert (np.max(get_prime_factors(self._Jx)) < 11)

        assert (self._Jx % 2 == 0)

        _x = np.linspace(self._x_min, self._x_max, self._Jx, endpoint=False)

        self._dx = _x[1] - _x[0]

        self._Lx = self._Jx * self._dx

        self._x = torch.tensor(_x, dtype=torch.float64, device=self._device)

    def init_external_potential(self, compute_external_potential, parameters_potential):

        self._compute_external_potential = compute_external_potential

        for key, p in parameters_potential.items():

            value = p[0]
            unit = p[1]

            if unit == 'm':
                _value = value / self._units.unit_length
            elif unit == 's':
                _value = value / self._units.unit_time
            elif unit == 'Hz':
                _value = value / self._units.unit_frequency
            else:
                raise Exception('unknown unit')

            self._p[key] = _value

    def set_external_potential(self, *, t, u):

        _t = t / self._units.unit_time

        self._V = self._compute_external_potential(self._x, t, u, self._p)

    def compute_ground_state_solution(self, *, n_atoms, n_iter, tau, adaptive_tau=True, return_residuals=False):

        _tau = tau / self._units.unit_time

        if n_iter < 2500:

            message = 'compute_ground_state_solution(self, **kwargs): n_iter should not be smaller than 2500'

            raise Exception(message)

        _psi_0, vec_res, vec_iter = qsolve_core_gpe_1d.compute_ground_state_solution(
            self._V,
            self._dx,
            _tau,
            adaptive_tau,
            n_iter,
            n_atoms,
            self._hbar,
            self._m_atom,
            self._g)

        if return_residuals:

            return self._units.unit_wave_function * _psi_0.cpu().numpy(), vec_res, vec_iter

        else:

            return self._units.unit_wave_function * _psi_0.cpu().numpy()

    def init_time_evolution(self, *, t_final, dt):

        self._t_final = t_final / self._units.unit_time
        self._dt = dt / self._units.unit_time

        self._n_time_steps = int(np.round(self._t_final / self._dt))

        self._n_times = self._n_time_steps + 1

        assert (np.abs(self._n_time_steps * self._dt - self._t_final)) < 1e-14

        self._times = self._dt * np.arange(self._n_times)

        assert (np.abs(self._times[-1] - self._t_final)) < 1e-14

    def propagate_gpe(self, *, u_of_times, n_start, n_inc, mue_shift=0.0):

        _mue_shift = mue_shift / self._units.unit_energy

        n_local = 0

        while n_local < n_inc:

            n = n_start + n_local

            self._t = self._times[n]

            if u_of_times.ndim > 1:

                _u = 0.5 * (u_of_times[:, n] + u_of_times[:, n + 1])

            else:

                _u = 0.5 * (u_of_times[n] + u_of_times[n + 1])

            self._V = self._compute_external_potential(self._x, self._t, _u, self._p)

            self._psi = qsolve_core_gpe_1d.propagate_gpe(
                self._psi,
                self._V,
                self._dx,
                self._dt,
                _mue_shift,
                self._hbar,
                self._m_atom,
                self._g)

            n_local = n_local + 1

    @property
    def x(self):
        return self._units.unit_length * self._x.cpu().numpy()

    @property
    def dx(self):
        return self._units.unit_length * self._dx

    @property
    def times(self):
        return self._units.unit_time * self._times

    @property
    def t(self):
        return self._units.unit_time * self._t

    @property
    def psi(self):
        return self._units.unit_wave_function * self._psi.cpu().numpy()

    @psi.setter
    def psi(self, value):
        self._psi = torch.tensor(value / self._units.unit_wave_function, device=self._device)

    @property
    def V(self):
        return self._units.unit_energy * self._V.cpu().numpy()

    def compute_n_atoms(self):
        return qsolve_core_gpe_1d.compute_n_atoms(self._psi, self._dx)

    def compute_chemical_potential(self):

        _mue = qsolve_core_gpe_1d.compute_chemical_potential(
            self._psi, self._V, self._dx, self._hbar, self._m_atom, self._g)

        return self._units.unit_energy * _mue

    def compute_total_energy(self):

        _E = qsolve_core_gpe_1d.compute_total_energy(self._psi, self._V, self._dx, self._hbar, self._m_atom, self._g)

        return self._units.unit_energy * _E

    def compute_kinetic_energy(self):

        _E_kinetic = qsolve_core_gpe_1d.compute_kinetic_energy(self._psi, self._dx, self._hbar, self._m_atom)

        return self._units.unit_energy * _E_kinetic

    def compute_potential_energy(self):

        _E_potential = qsolve_core_gpe_1d.compute_potential_energy(self._psi, self._V, self._dx)

        return self._units.unit_energy * _E_potential

    def compute_interaction_energy(self):

        _E_interaction = qsolve_core_gpe_1d.compute_interaction_energy(self._psi, self._dx, self._g)

        return self._units.unit_energy * _E_interaction
