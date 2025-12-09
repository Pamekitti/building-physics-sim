"""
Steady-state heat balance via thermal circuit analogy.
Q = dT/R at each branch, Kirchhoff at indoor node.
"""

import numpy as np
import pandas as pd
from config import RHO_AIR, CP_AIR, H_E


def cos_inc(zenith: np.ndarray, azimuth_sun: np.ndarray, tilt: float, azimuth_surf: float) -> np.ndarray:
    """Calculate cosine of incidence angle."""
    zenith_rad = np.deg2rad(zenith)
    azimuth_sun_rad = np.deg2rad(azimuth_sun)
    tilt_rad = np.deg2rad(tilt)
    azimuth_surf_rad = np.deg2rad(azimuth_surf)
    return np.sin(zenith_rad)*np.sin(tilt_rad)*np.cos(azimuth_sun_rad - azimuth_surf_rad) + np.cos(zenith_rad)*np.cos(tilt_rad)


def irradiance_on_plane(I_dir: np.ndarray, I_dif: np.ndarray, cos_i: np.ndarray, tilt: float) -> np.ndarray:
    """Calculate total irradiance on tilted plane."""
    F_sky = (1 + np.cos(np.deg2rad(tilt))) / 2
    I_beam: np.ndarray = I_dir * np.maximum(0, cos_i)
    return np.maximum(0, I_beam) + I_dif * F_sky


def sol_air(T_out: np.ndarray, I_sol: np.ndarray, alpha: float, h_e: float) -> np.ndarray:
    """Calculate sol-air temperature."""
    return T_out + alpha * I_sol / h_e


def run_hourly(weather: pd.DataFrame, planes: list, air, T_set, vent_ACH, gains) -> pd.DataFrame:
    """Run hourly steady-state simulation."""

    weather: pd.DataFrame = weather.copy().reset_index(drop=True)
    n_hours = len(weather)

    T_out: np.ndarray = weather['T_out_C'].values
    T_in: np.ndarray = np.full(n_hours, T_set) if np.isscalar(T_set) else np.asarray(T_set)

    if vent_ACH is None:
        vent_ACH = 0.0
    vent: np.ndarray = np.full(n_hours, vent_ACH) if np.isscalar(vent_ACH) else np.asarray(vent_ACH)

    Q_roof: np.ndarray = np.zeros(n_hours)
    Q_walls: np.ndarray = np.zeros(n_hours)
    Q_solar: np.ndarray = np.zeros(n_hours)

    # Parallel windows resistance
    R_win = 1.0 / sum(p.area / p.r for p in planes if p.is_window())

    # Infiltration resistance
    Vdot_inf = air.infiltration * air.volume / 3600
    R_inf = 1.0 / (RHO_AIR * CP_AIR * Vdot_inf) if Vdot_inf > 0 else np.inf

    # Ventilation resistance (time-varying)
    Vdot_vent: np.ndarray = vent * air.volume / 3600
    R_vent: np.ndarray = np.where(Vdot_vent > 0, 1.0 / (RHO_AIR * CP_AIR * Vdot_vent), np.inf)

    # Solar angles
    theta_s: np.ndarray = weather['theta_s_deg'].values
    phi_s: np.ndarray = weather['phi_s_deg'].values
    I_dir: np.ndarray = weather['I_dir_Wm2'].values
    I_dif: np.ndarray = weather['I_dif_Wm2'].values

    for plane in planes:
        cos_i: np.ndarray = cos_inc(theta_s, phi_s, plane.tilt, plane.azimuth)
        I_sol: np.ndarray = irradiance_on_plane(I_dir, I_dif, cos_i, plane.tilt)

        if plane.is_opaque():
            T_sa: np.ndarray = sol_air(T_out, I_sol, plane.alpha, H_E)
            Q: np.ndarray = (T_in - T_sa) / plane.R()
            if plane.tilt == 0:
                Q_roof += Q
            else:
                Q_walls += Q

        elif plane.is_window():
            Q_solar += plane.g * plane.area * I_sol * plane.F_sh

    Q_win: np.ndarray = (T_in - T_out) / R_win
    Q_inf: np.ndarray = (T_in - T_out) / R_inf
    Q_vent: np.ndarray = (T_in - T_out) / R_vent

    Q_int = gains.total() * 1000 if gains else 0.0

    Q_heat: np.ndarray = np.maximum(0, Q_roof + Q_walls + Q_win + Q_inf + Q_vent - Q_solar - Q_int)

    return pd.DataFrame({
        'timestamp': weather['timestamp'],
        'T_out_C': T_out,
        'T_int_C': T_in,
        'vent_ACH': vent,
        'Q_roof_W': Q_roof,
        'Q_walls_W': Q_walls,
        'Q_win_W': Q_win,
        'Q_inf_W': Q_inf,
        'Q_vent_W': Q_vent,
        'Q_solar_W': Q_solar,
        'Q_int_W': Q_int,
        'Q_heat_W': Q_heat,
    })
