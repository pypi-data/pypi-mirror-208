def eval_potential_harmonic_3d(x_3d, y_3d, z_3d, omega_x, omega_y, omega_z, m_atom):

    V = 0.5 * m_atom * (omega_x**2 * x_3d**2 + omega_y**2 * y_3d**2 + omega_z**2 * z_3d**2)

    return V
