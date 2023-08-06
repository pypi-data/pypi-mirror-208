def eval_potential_harmonic_y_3d(y_3d, omega_y, m_atom):

    V = 0.5 * m_atom * omega_y**2 * y_3d**2

    return V
