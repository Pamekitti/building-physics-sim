import numpy as np
import pandas as pd
from config import RHO_AIR, CP_AIR, H_E


def cos_incidence(theta_s_deg, phi_s_deg, tilt_deg, azimuth_deg):
    # cos(incidence angle) for plane
    ths = np.deg2rad(theta_s_deg)
    phs = np.deg2rad(phi_s_deg)
    thp = np.deg2rad(tilt_deg)
    php = np.deg2rad(azimuth_deg)
    return np.sin(ths) * np.sin(thp) * np.cos(phs - php) + np.cos(ths) * np.cos(thp)


def plane_irradiance(I_dir, I_dif, cos_i, tilt):
    # Total irradiance on tilted plane
    cos_tilt = np.cos(np.deg2rad(tilt))
    F_sky = (1.0 + cos_tilt) / 2.0
    return np.maximum(0.0, I_dir * np.maximum(0.0, cos_i)) + I_dif * F_sky


def sol_air_temp(T_out, I_p, alpha, epsilon, I_LW, h_e):
    # Sol-air temperature calculation (simplified ASHRAE approach)
    # Ignores longwave radiation effects for simplicity (standard practice)
    # T_sol = T_out + (alpha * I_solar) / h_e
    # This ensures T_sol >= T_out always
    return T_out + (alpha * I_p) / h_e


def run_hourly(weather, planes, air, T_heat, T_cool, gains=None, kitchen_kw=0.0, kitchen_on=None):
    # Calculate hourly loads
    req_cols = ['timestamp','T_out_C','I_dir_Wm2','I_dif_Wm2','theta_s_deg','phi_s_deg']
    for col in req_cols:
        if col not in weather.columns:
            raise ValueError(f"Missing: {col}")

    w = weather.copy().reset_index(drop=True)
    n = len(w)
    I_LW = w['I_LW_Wm2'].values if 'I_LW_Wm2' in w.columns else None
    T_gnd = w['T_ground_C'].values if 'T_ground_C' in w.columns else None

    Q_trans_h = np.zeros(n)
    Q_trans_c = np.zeros(n)
    Q_solar = np.zeros(n)

    # Calculate loads for each plane
    for p in planes:
        cos_i = cos_incidence(w['theta_s_deg'].values, w['phi_s_deg'].values, p.tilt_deg, p.azimuth_deg)
        I_p = plane_irradiance(w['I_dir_Wm2'].values, w['I_dif_Wm2'].values, cos_i, p.tilt_deg)

        if p.is_opaque():
            if p.ground_contact:
                if T_gnd is None:
                    raise ValueError(f"{p.name} needs T_ground_C")
                T_boundary_h = T_gnd
                T_boundary_c = T_gnd
            else:
                if p.alpha is None or p.epsilon is None:
                    raise ValueError(f"{p.name} needs alpha/epsilon")

                # Heating: use T_out (conservative - ignore solar gains)
                T_boundary_h = w['T_out_C'].values

                # Cooling: use T_sol only if T_sol > T_out (conservative - ignore radiative cooling)
                T_sol = sol_air_temp(w['T_out_C'].values, I_p, p.alpha, p.epsilon, I_LW, H_E)
                T_boundary_c = np.maximum(T_sol, w['T_out_C'].values)

            Q_trans_h += p.U * p.area_m2 * (T_boundary_h - T_heat)

            # For cooling: ground contact should not provide free cooling (only count if it's a heat gain)
            if p.ground_contact:
                Q_trans_c += np.maximum(0.0, p.U * p.area_m2 * (T_boundary_c - T_cool))
            else:
                Q_trans_c += p.U * p.area_m2 * (T_boundary_c - T_cool)

        elif p.is_window():
            Q_trans_h += p.U * p.area_m2 * (w['T_out_C'].values - T_heat)
            Q_trans_c += p.U * p.area_m2 * (w['T_out_C'].values - T_cool)
            if p.g is None:
                raise ValueError(f"{p.name} needs g")
            Fsh = 1.0 if p.F_sh is None else p.F_sh
            Q_solar += p.g * p.area_m2 * I_p * Fsh

    # Air loads
    V_inf = air.ACH_infiltration_h * air.V_zone_m3 / 3600.0
    Q_air_h = RHO_AIR * CP_AIR * (air.Vdot_vent_m3s * (1.0 - air.eta_HRV) + V_inf) * (w['T_out_C'].values - T_heat)
    Q_air_c = RHO_AIR * CP_AIR * (air.Vdot_vent_m3s * (1.0 - air.eta_HRV) + V_inf) * (w['T_out_C'].values - T_cool)

    # Internal gains
    Q_int = np.zeros(n)
    if gains:
        Q_int = gains.total_kw() * 1000.0 * np.ones(n)

    Q_kitchen = np.zeros(n)
    if kitchen_kw > 0.0 and kitchen_on is not None:
        k = kitchen_on.astype(bool).to_numpy()
        Q_kitchen[k] = kitchen_kw * 1000.0

    # Sign convention: heat INTO building = positive, heat OUT = negative
    # Q_trans_h and Q_air_h are naturally negative when T_out < T_in (heat out)
    # All gains are positive (heat entering)

    # Heating load needed (positive value)
    # Conservative design: exclude solar/internal gains (worst-case = no free heat)
    Q_heat = np.maximum(0.0, -Q_trans_h - Q_air_h)

    # Cooling load needed (positive value)
    # Realistic design: include all heat gains
    Q_cool = np.maximum(0.0, Q_trans_c + Q_air_c + Q_solar + Q_int + Q_kitchen)

    df = pd.DataFrame({
        'timestamp': w['timestamp'],
        'T_out_C': w['T_out_C'],
        'Q_trans_h_W': Q_trans_h,     # negative (heat out)
        'Q_air_h_W': Q_air_h,         # negative (heat out)
        'Q_heat_W': Q_heat,           # positive (energy added)
        'Q_trans_c_W': Q_trans_c,     # positive (heat in)
        'Q_air_c_W': Q_air_c,         # positive (heat in)
        'Q_solar_W': Q_solar,         # positive (heat in)
        'Q_int_W': Q_int,             # positive (heat in)
        'Q_kitchen_W': Q_kitchen,     # positive (heat in)
        'Q_cool_W': Q_cool,           # positive (energy removed)
    })

    # Add solar and IR data if available
    if 'theta_s_deg' in w.columns:
        df['theta_s_deg'] = w['theta_s_deg']
    if 'I_LW_Wm2' in w.columns:
        df['I_LW_Wm2'] = w['I_LW_Wm2']

    return df
