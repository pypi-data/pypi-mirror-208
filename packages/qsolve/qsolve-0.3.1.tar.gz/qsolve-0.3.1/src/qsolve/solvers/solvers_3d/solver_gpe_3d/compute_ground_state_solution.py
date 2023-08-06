from qsolve.core import qsolve_core_gpe_3d


def compute_ground_state_solution(self, kwargs):

    tau = kwargs["tau"] / self.units.unit_time

    n_iter = kwargs["n_iter"]

    if n_iter < 2500:

        message = 'compute_ground_state_solution(self, **kwargs): n_iter should not be smaller than 2500'

        raise Exception(message)

    if "adaptive_tau" in kwargs:

        adaptive_tau = kwargs["adaptive_tau"]

    else:

        adaptive_tau = True

    N = kwargs["N"]

    psi_0, vec_res, vec_iter = qsolve_core_gpe_3d.compute_ground_state_solution(
        self.V,
        self.dx,
        self.dy,
        self.dz,
        tau,
        adaptive_tau,
        n_iter,
        N,
        self.hbar,
        self.m_atom,
        self.g)

    self.psi_0 = psi_0

    self.vec_res_ground_state_computation = vec_res
    self.vec_iter_ground_state_computation = vec_iter
