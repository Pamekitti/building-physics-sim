"""
Steady-state heat balance via thermal circuit analogy.
Q = dT/R at each branch, Kirchhoff at indoor node.
"""

import numpy as np
import pandas as pd
from config import RHO_AIR, CP_AIR, H_E


def cos_inc(zenith, azimuth_sun, tilt, azimuth_surf):
    zs = np.deg2rad(zenith)
    az_s = np.deg2rad(azimuth_sun)
    t = np.deg2rad(tilt)
    az_p = np.deg2rad(azimuth_surf)
    return np.sin(zs)*np.sin(t)*np.cos(az_s - az_p) + np.cos(zs)*np.cos(t)


def irradiance_on_plane(I_dir, I_dif, cos_i, tilt):
    F_sky = (1 + np.cos(np.deg2rad(tilt))) / 2
    I_beam = I_dir * np.maximum(0, cos_i)
    return np.maximum(0, I_beam) + I_dif * F_sky


def sol_air(T_out, I_sol, alpha, h_e):
    return T_out + alpha * I_sol / h_e


def run_hourly(weather, planes, air, T_set, vent_ACH=None, gains=None):
    w = weather.copy().reset_index(drop=True)
    n = len(w)
    T_out = w['T_out_C'].values

    T_in = np.full(n, T_set) if np.isscalar(T_set) else np.asarray(T_set)

    if vent_ACH is None:
        vent_ACH = 0.0
    vent = np.full(n, vent_ACH) if np.isscalar(vent_ACH) else np.asarray(vent_ACH)

    Q_roof = np.zeros(n)
    Q_walls = np.zeros(n)
    Q_solar = np.zeros(n)

    # parallel windows
    R_win = 1.0 / sum(p.area / p.r for p in planes if p.is_window())

    # infiltration
    Vdot_inf = air.infiltration * air.volume / 3600
    R_inf = 1.0 / (RHO_AIR * CP_AIR * Vdot_inf) if Vdot_inf > 0 else np.inf

    # ventilation (time-varying)
    Vdot_vent = vent * air.volume / 3600
    R_vent = np.where(Vdot_vent > 0, 1.0 / (RHO_AIR * CP_AIR * Vdot_vent), np.inf)

    for p in planes:
        ci = cos_inc(w['theta_s_deg'].values, w['phi_s_deg'].values, p.tilt, p.azimuth)
        I_sol = irradiance_on_plane(w['I_dir_Wm2'].values, w['I_dif_Wm2'].values, ci, p.tilt)

        if p.is_opaque():
            T_sa = sol_air(T_out, I_sol, p.alpha, H_E)
            Q = (T_in - T_sa) / p.R()
            if p.tilt == 0:
                Q_roof += Q
            else:
                Q_walls += Q

        elif p.is_window():
            Q_solar += p.g * p.area * I_sol * p.F_sh

    Q_win = (T_in - T_out) / R_win
    Q_inf = (T_in - T_out) / R_inf
    Q_vent = (T_in - T_out) / R_vent

    Q_int = gains.total() * 1000 if gains else 0.0

    Q_heat = np.maximum(0, Q_roof + Q_walls + Q_win + Q_inf + Q_vent - Q_solar - Q_int)

    return pd.DataFrame({
        'timestamp': w['timestamp'], 'T_out_C': T_out,
        'T_int_C': T_in, 'vent_ACH': vent,
        'Q_roof_W': Q_roof, 'Q_walls_W': Q_walls,
        'Q_win_W': Q_win, 'Q_inf_W': Q_inf, 'Q_vent_W': Q_vent,
        'Q_solar_W': Q_solar, 'Q_int_W': Q_int, 'Q_heat_W': Q_heat,
    })
