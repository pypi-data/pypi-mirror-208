"""
Implementation of a Lesanovsky - type potential corresponding to the article: Adiabatic radio - frequency potentials
for the coherent manipulation of matter waves, PHYSICAL REVIEW A 73, 03361 9(2006)
"""

import torch
import math


def eval_potential_lesanovsky_3d(x_3d, y_3d, z_3d, g_F, m_F, m_F_prime, omega_perp, omega_para, omega_delta_detuning,
                                 omega_trap_bottom, omega_rabi, hbar, mu_B, m_atom):

    kappa = g_F * mu_B

    # radio - frequency
    omega_rf = omega_trap_bottom + omega_delta_detuning

    # =============================================================================================
    # static part of B

    # Eq.(7.27) in Thorsten Schumm 's phd-thesis

    B0 = math.fabs((hbar * omega_trap_bottom) / (g_F * mu_B))

    # Eq.(3.8) in Thorsten Schumm 's phd-thesis
    B1 = math.fabs(math.sqrt((m_atom * omega_perp * omega_perp * B0) / (m_F * g_F * mu_B)))

    # Eq.(3.8) in Thorsten Schumm 's phd-thesis
    B2 = math.fabs((m_atom * omega_para * omega_para) / (m_F * g_F * mu_B))

    # ---------------------------------------------------------------------------------------------
    B_static_x = B1 * x_3d - (B2 / 2) * x_3d * z_3d
    B_static_y = -B1 * y_3d - (B2 / 2) * y_3d * z_3d
    B_static_z = B0 + (B2 / 2) * (z_3d * z_3d - 0.5 * (x_3d * x_3d + y_3d * y_3d))

    norm_B_static = torch.sqrt(B_static_x * B_static_x + B_static_y * B_static_y + B_static_z * B_static_z)
    # ---------------------------------------------------------------------------------------------
    # =============================================================================================

    tmp = (norm_B_static - hbar * omega_rf / math.fabs(kappa))

    resonance_term = tmp * tmp

    # --------------------------------------------------------------------------------------------
    # Eq.(7.4) in Thorsten Schumm 's phd thesis

    B_rf_x = ((2 * hbar * omega_rabi) / (g_F * mu_B))
    B_rf_y = 0.0
    B_rf_z = 0.0
    # --------------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------------------
    # get perpendicular RF field

    B_rf_perp_x = 0.0
    B_rf_perp_y = B_rf_x * B_static_z
    B_rf_perp_z = -B_rf_x * B_static_y

    # B_rf_perp_x = B_rf_perp_x / norm_B_static
    B_rf_perp_y = B_rf_perp_y / norm_B_static
    B_rf_perp_z = B_rf_perp_z / norm_B_static
    # --------------------------------------------------------------------------------------------

    coupling_term = 0.25 * (B_rf_perp_y * B_rf_perp_y + B_rf_perp_z * B_rf_perp_z)

    V = m_F_prime * kappa * torch.sqrt(resonance_term + coupling_term)

    V = V - torch.min(V)

    return V
