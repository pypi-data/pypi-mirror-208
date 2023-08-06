def eval_potential_harmonic_2d(x_2d, y_2d, omega_x, omega_y, m_atom):

    V = 0.5 * m_atom * (omega_x**2 * x_2d**2 + omega_y**2 * y_2d**2)

    return V
