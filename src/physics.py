"""
Steady-state heat balance using thermal circuit analogy.
Q = dT / R (Ohm's law), Kirchhoff at indoor node
"""

import numpy as np
import pandas as pd
from config import RHO_AIR, CP_AIR, H_E


def cos_incidence(theta_s, phi_s, tilt, azimuth):
    ths = np.deg2rad(theta_s)
    phs = np.deg2rad(phi_s)
    thp = np.deg2rad(tilt)
    php = np.deg2rad(azimuth)
    return np.sin(ths)*np.sin(thp)*np.cos(phs - php) + np.cos(ths)*np.cos(thp)


def plane_irradiance(I_dir, I_dif, cos_i, tilt):
    F_sky = (1 + np.cos(np.deg2rad(tilt))) / 2
    return np.maximum(0, I_dir * np.maximum(0, cos_i)) + I_dif * F_sky


def sol_air_temp(T_ext, I_sol, alpha, h_ext):
    return T_ext + alpha * I_sol / h_ext


def run_hourly(weather, planes, air, T_int, vent_ACH=None, gains=None):
    req = ['timestamp', 'T_out_C', 'I_dir_Wm2', 'I_dif_Wm2', 'theta_s_deg', 'phi_s_deg']
    for c in req:
        if c not in weather.columns:
            raise ValueError(f"Missing: {c}")

    w = weather.copy().reset_index(drop=True)
    n = len(w)
    T_ext = w['T_out_C'].values

    if np.isscalar(T_int):
        T_int = np.full(n, T_int)
    else:
        T_int = np.asarray(T_int)

    if vent_ACH is None:
        vent_ACH = 0.0
    vent_arr = np.full(n, vent_ACH) if np.isscalar(vent_ACH) else np.asarray(vent_ACH)

    Q_roof = np.zeros(n)
    Q_walls = np.zeros(n)
    Q_solar = np.zeros(n)

    # window conductance
    UA_win = sum(p.U * p.area_m2 for p in planes if p.is_window())

    # infiltration (fixed)
    Vdot_inf = air.ACH_infiltration_h * air.V_zone_m3 / 3600
    UA_inf = RHO_AIR * CP_AIR * Vdot_inf

    # ventilation (variable)
    Vdot_vent = vent_arr * air.V_zone_m3 / 3600
    UA_vent = RHO_AIR * CP_AIR * Vdot_vent

    for p in planes:
        cos_i = cos_incidence(w['theta_s_deg'].values, w['phi_s_deg'].values,
                              p.tilt_deg, p.azimuth_deg)
        I_sol = plane_irradiance(w['I_dir_Wm2'].values, w['I_dif_Wm2'].values,
                                 cos_i, p.tilt_deg)

        if p.is_opaque():
            R = 1 / (p.U * p.area_m2)
            T_sol = sol_air_temp(T_ext, I_sol, p.alpha, H_E)
            Q = (T_int - T_sol) / R

            if p.tilt_deg == 0:
                Q_roof += Q
            else:
                Q_walls += Q

        elif p.is_window():
            F_sh = p.F_sh if p.F_sh else 1.0
            Q_solar += p.g * p.area_m2 * I_sol * F_sh

    Q_win = (T_int - T_ext) * UA_win
    Q_inf = (T_int - T_ext) * UA_inf
    Q_vent = (T_int - T_ext) * UA_vent

    Q_int = np.zeros(n)
    if gains:
        Q_int = gains.total_kw() * 1000 * np.ones(n)

    # energy balance
    Q_heat = np.maximum(0, Q_roof + Q_walls + Q_win + Q_inf + Q_vent - Q_solar - Q_int)

    out = pd.DataFrame({
        'timestamp': w['timestamp'], 'T_out_C': w['T_out_C'],
        'T_int_C': T_int, 'vent_ACH': vent_arr,
        'Q_roof_W': Q_roof, 'Q_walls_W': Q_walls,
        'Q_win_W': Q_win, 'Q_inf_W': Q_inf, 'Q_vent_W': Q_vent,
        'Q_solar_W': Q_solar, 'Q_int_W': Q_int, 'Q_heat_W': Q_heat,
    })
    out.attrs['UA_win'] = UA_win
    out.attrs['UA_inf'] = UA_inf
    return out
