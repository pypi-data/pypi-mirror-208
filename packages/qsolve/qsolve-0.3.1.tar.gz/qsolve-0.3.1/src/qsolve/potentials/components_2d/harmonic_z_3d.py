def eval_potential_harmonic_z_3d(z_3d, omega_z, m_atom):

    V = 0.5 * m_atom * omega_z**2 * z_3d**2

    return V
