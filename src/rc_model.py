# RC model for building thermal simulation
# 3-resistance model following Gori (2017) Equation 3.5

import numpy as np
import pandas as pd
from src.physics import cos_inc, irradiance_on_plane
from config import RHO_AIR, CP_AIR


def calc_T_C(T_C_prev, T_int_curr, T_int_prev, T_ext_curr, T_ext_prev,
             I_sol_curr, I_sol_prev, R1, R2, R3, C, alpha, tau) -> float:
    """
    Calculate thermal mass temperature at current timestep using 3-resistance model.

    From Gori (2017) Eq 3.5, after eliminating surface node T_s:

    T_C^p = [  (T_int^p + T_int^{p-1})/R1
             + (T_ext^p + T_ext^{p-1})/(R2+R3)
             + alpha * R3/(R2+R3) * (I_sol^p + I_sol^{p-1})
             + (2C/tau - 1/R1 - 1/(R2+R3)) * T_C^{p-1}
            ] / (2C/tau + 1/R1 + 1/(R2+R3))

    R1: thermal mass to indoor (m²K/W)
    R2: thermal mass to external surface node (m²K/W)
    R3: external surface resistance = 1/h_ext (m²K/W)
    C: thermal capacitance per unit area (J/m²K)
    alpha: solar absorptance
    tau: timestep (s)
    """
    R_ext = R2 + R3
    solar_factor = alpha * R3 / R_ext

    numerator = ((T_int_curr + T_int_prev) / R1 +
                 (T_ext_curr + T_ext_prev) / R_ext +
                 solar_factor * (I_sol_curr + I_sol_prev) +
                 (2*C/tau - 1/R1 - 1/R_ext) * T_C_prev)
    denominator = 2*C/tau + 1/R1 + 1/R_ext
    return numerator / denominator


def calc_heat_flux(T_C: np.ndarray, T_int: np.ndarray, R1) -> np.ndarray:
    """
    Calculate heat flux from thermal mass to indoor air.

    q = (T_C - T_int) / R1  [W/m²]

    Positive = heat into room, Negative = heat out of room
    """
    return (T_C - T_int) / R1


def run_rc_hourly(
    weather: pd.DataFrame,
    envelope: dict,
    air,
    T_set: float,
    vent_ACH: float,
    gains,
    dt_minutes: int = 15
) -> pd.DataFrame:
    """Run RC simulation for building with specified timestep."""

    # Interpolate weather to finer timestep
    weather_hourly: pd.DataFrame = weather.copy().reset_index(drop=True)
    weather_hourly = weather_hourly.set_index('timestamp')

    # Resample to dt_minutes intervals
    weather_interp = weather_hourly.resample(f'{dt_minutes}min').interpolate(method='linear')
    weather_interp = weather_interp.reset_index()

    n_steps = len(weather_interp)
    tau = dt_minutes * 60  # Convert to seconds

    T_out: np.ndarray = weather_interp['T_out_C'].values
    T_int: np.ndarray = np.full(n_steps, T_set)

    roof = envelope['roof']
    walls = envelope['walls']
    windows = envelope['windows']

    # Solar irradiance on each surface
    theta_s: np.ndarray = weather_interp['theta_s_deg'].values
    phi_s: np.ndarray = weather_interp['phi_s_deg'].values
    I_dir: np.ndarray = weather_interp['I_dir_Wm2'].values
    I_dif: np.ndarray = weather_interp['I_dif_Wm2'].values

    cos_i_roof: np.ndarray = cos_inc(theta_s, phi_s, 0, 0)
    cos_i_N: np.ndarray = cos_inc(theta_s, phi_s, 90, 0)
    cos_i_S: np.ndarray = cos_inc(theta_s, phi_s, 90, 180)
    cos_i_E: np.ndarray = cos_inc(theta_s, phi_s, 90, 90)
    cos_i_W: np.ndarray = cos_inc(theta_s, phi_s, 90, 270)

    I_sol_roof: np.ndarray = irradiance_on_plane(I_dir, I_dif, cos_i_roof, 0)
    I_sol_N: np.ndarray = irradiance_on_plane(I_dir, I_dif, cos_i_N, 90)
    I_sol_S: np.ndarray = irradiance_on_plane(I_dir, I_dif, cos_i_S, 90)
    I_sol_E: np.ndarray = irradiance_on_plane(I_dir, I_dif, cos_i_E, 90)
    I_sol_W: np.ndarray = irradiance_on_plane(I_dir, I_dif, cos_i_W, 90)

    T_init = 10.0
    T_C_roof: np.ndarray = np.full(n_steps, T_init)
    T_C_N: np.ndarray = np.full(n_steps, T_init)
    T_C_S: np.ndarray = np.full(n_steps, T_init)
    T_C_E: np.ndarray = np.full(n_steps, T_init)
    T_C_W: np.ndarray = np.full(n_steps, T_init)

    # Time stepping
    for p in range(1, n_steps):
        T_C_roof[p] = calc_T_C(
            T_C_roof[p-1], T_int[p], T_int[p-1], T_out[p], T_out[p-1],
            I_sol_roof[p], I_sol_roof[p-1],
            roof['R1'], roof['R2'], roof['R3'], roof['C'], roof['alpha'], tau)
        T_C_N[p] = calc_T_C(
            T_C_N[p-1], T_int[p], T_int[p-1], T_out[p], T_out[p-1],
            I_sol_N[p], I_sol_N[p-1],
            walls['N']['R1'], walls['N']['R2'], walls['N']['R3'], walls['N']['C'], walls['N']['alpha'], tau)
        T_C_S[p] = calc_T_C(
            T_C_S[p-1], T_int[p], T_int[p-1], T_out[p], T_out[p-1],
            I_sol_S[p], I_sol_S[p-1],
            walls['S']['R1'], walls['S']['R2'], walls['S']['R3'], walls['S']['C'], walls['S']['alpha'], tau)
        T_C_E[p] = calc_T_C(
            T_C_E[p-1], T_int[p], T_int[p-1], T_out[p], T_out[p-1],
            I_sol_E[p], I_sol_E[p-1],
            walls['E']['R1'], walls['E']['R2'], walls['E']['R3'], walls['E']['C'], walls['E']['alpha'], tau)
        T_C_W[p] = calc_T_C(
            T_C_W[p-1], T_int[p], T_int[p-1], T_out[p], T_out[p-1],
            I_sol_W[p], I_sol_W[p-1],
            walls['W']['R1'], walls['W']['R2'], walls['W']['R3'], walls['W']['C'], walls['W']['alpha'], tau)

    # Heat flux from thermal mass to indoor (W/m²)
    q_roof: np.ndarray = calc_heat_flux(T_C_roof, T_int, roof['R1'])
    q_N: np.ndarray = calc_heat_flux(T_C_N, T_int, walls['N']['R1'])
    q_S: np.ndarray = calc_heat_flux(T_C_S, T_int, walls['S']['R1'])
    q_E: np.ndarray = calc_heat_flux(T_C_E, T_int, walls['E']['R1'])
    q_W: np.ndarray = calc_heat_flux(T_C_W, T_int, walls['W']['R1'])

    # Heat loss through envelope (W) - multiply by area, flip sign
    Q_roof: np.ndarray = -q_roof * roof['area']
    Q_N: np.ndarray = -q_N * walls['N']['area']
    Q_S: np.ndarray = -q_S * walls['S']['area']
    Q_E: np.ndarray = -q_E * walls['E']['area']
    Q_W: np.ndarray = -q_W * walls['W']['area']
    Q_walls: np.ndarray = Q_N + Q_S + Q_E + Q_W

    # Windows (steady state)
    U_win = 1.0 / windows['R']
    Q_win: np.ndarray = U_win * windows['area'] * (T_int - T_out)

    # Window solar gains
    cos_i_win: np.ndarray = cos_inc(theta_s, phi_s, 90, 180)
    I_sol_win: np.ndarray = irradiance_on_plane(I_dir, I_dif, cos_i_win, 90)
    Q_solar: np.ndarray = windows['g'] * windows['area'] * I_sol_win

    # Infiltration
    Vdot_inf = air.infiltration * air.volume / 3600
    Q_inf: np.ndarray = RHO_AIR * CP_AIR * Vdot_inf * (T_int - T_out)

    # Ventilation
    Vdot_vent = vent_ACH * air.volume / 3600
    if Vdot_vent > 0:
        Q_vent: np.ndarray = RHO_AIR * CP_AIR * Vdot_vent * (T_int - T_out)
    else:
        Q_vent: np.ndarray = np.zeros(n_steps)

    # Internal gains
    Q_int = gains.total() * 1000

    # Heating demand
    Q_heat: np.ndarray = np.maximum(0, Q_roof + Q_walls + Q_win + Q_inf + Q_vent - Q_solar - Q_int)

    return pd.DataFrame({
        'timestamp': weather_interp['timestamp'],
        'T_out_C': T_out,
        'T_int_C': T_int,
        'T_C_roof': T_C_roof,
        'T_C_N': T_C_N,
        'T_C_S': T_C_S,
        'T_C_E': T_C_E,
        'T_C_W': T_C_W,
        'I_sol_roof': I_sol_roof,
        'I_sol_S': I_sol_S,
        'Q_roof_W': Q_roof,
        'Q_walls_W': Q_walls,
        'Q_win_W': Q_win,
        'Q_inf_W': Q_inf,
        'Q_vent_W': Q_vent,
        'Q_solar_W': Q_solar,
        'Q_int_W': Q_int,
        'Q_heat_W': Q_heat,
    })
