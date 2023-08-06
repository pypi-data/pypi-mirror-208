def eval_potential_harmonic_x_3d(x_3d, omega_x, m_atom):

    V = 0.5 * m_atom * omega_x**2 * x_3d**2

    return V
