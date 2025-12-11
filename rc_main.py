#!/usr/bin/env python3
# Compare lightweight vs heavyweight buildings with RC model
# 3-resistance model following Gori (2017)

import os
import pandas as pd

from config import (
    BUILDING_VOLUME,
    AREA_ROOF, AREA_WALL_N, AREA_WALL_S, AREA_WALL_E, AREA_WALL_W, AREA_WINDOW,
    WINDOW_R, ALPHA, SHGC, INFILTRATION_ACH, INTERNAL_GAIN_W
)
from config_heavyweight import (
    WALL_R1_LW, WALL_R2_LW, WALL_R3_LW, WALL_CA_LW,
    WALL_R1_HW, WALL_R2_HW, WALL_R3_HW, WALL_CA_HW,
    ROOF_R1, ROOF_R2, ROOF_R3, ROOF_CA_LW, ROOF_CA_HW,
    C_WALL_LW, C_WALL_HW, C_ROOF_LW, C_ROOF_HW
)
from src.building import AirSide, InternalGains
from src.weather import load_epw_weather
from src.rc_model import run_rc_hourly
from src.rc_plots import (plot_glasgow_weather, plot_rc_heatup_week, plot_rc_shoulder_week,
                          plot_rc_shoulder_heating, plot_heating_histogram,
                          plot_heating_comparison_histogram, plot_monthly_peak_demand)


def build_envelope_3r(wall_R1, wall_R2, wall_R3, wall_CA,
                      roof_R1, roof_R2, roof_R3, roof_CA) -> dict:
    """Build envelope parameters for 3-resistance RC model.

    R1: thermal mass to indoor (m²K/W)
    R2: thermal mass to external surface node (m²K/W)
    R3: external surface resistance (m²K/W)
    CA: thermal capacitance per unit area (kJ/m²K)
    """
    # Convert C/A from kJ/m²K to J/m²K
    wall_C = wall_CA * 1000
    roof_C = roof_CA * 1000

    # Roof
    roof = {
        'R1': roof_R1,
        'R2': roof_R2,
        'R3': roof_R3,
        'C': roof_C,
        'alpha': ALPHA,
        'area': AREA_ROOF,
    }

    # Walls - same R values per unit area, different areas
    wall_N = {'R1': wall_R1, 'R2': wall_R2, 'R3': wall_R3, 'C': wall_C, 'alpha': ALPHA, 'area': AREA_WALL_N}
    wall_S = {'R1': wall_R1, 'R2': wall_R2, 'R3': wall_R3, 'C': wall_C, 'alpha': ALPHA, 'area': AREA_WALL_S}
    wall_E = {'R1': wall_R1, 'R2': wall_R2, 'R3': wall_R3, 'C': wall_C, 'alpha': ALPHA, 'area': AREA_WALL_E}
    wall_W = {'R1': wall_R1, 'R2': wall_R2, 'R3': wall_R3, 'C': wall_C, 'alpha': ALPHA, 'area': AREA_WALL_W}

    # Windows (steady state, no thermal mass)
    windows = {
        'R': WINDOW_R,
        'area': AREA_WINDOW,
        'g': SHGC,
    }

    envelope = {
        'roof': roof,
        'walls': {'N': wall_N, 'S': wall_S, 'E': wall_E, 'W': wall_W},
        'windows': windows,
    }
    return envelope


def run_simulations() -> tuple:
    """Run RC simulations for lightweight and heavyweight buildings."""

    # Load weather
    print("Loading weather...")
    weather: pd.DataFrame = load_epw_weather(
        'weather_files/GBR_SCT_Glasgow.AP.031400_TMYx/GBR_SCT_Glasgow.AP.031400_TMYx.epw',
        'weather_files/solarposition_data_Glasgow.csv'
    )
    weather['timestamp'] = pd.to_datetime({
        'year': 2021,
        'month': weather['timestamp'].dt.month,
        'day': weather['timestamp'].dt.day,
        'hour': weather['timestamp'].dt.hour
    })
    weather = weather.sort_values('timestamp').reset_index(drop=True)

    # Building parameters (same as Task 1)
    air = AirSide(BUILDING_VOLUME, 0.0, 0.0, INFILTRATION_ACH)
    gains = InternalGains(INTERNAL_GAIN_W / 1000)
    T_set = 21.0
    vent_ACH = 0.5

    # Build envelopes with 3-resistance model
    env_lw: dict = build_envelope_3r(
        WALL_R1_LW, WALL_R2_LW, WALL_R3_LW, WALL_CA_LW,
        ROOF_R1, ROOF_R2, ROOF_R3, ROOF_CA_LW
    )
    env_hw: dict = build_envelope_3r(
        WALL_R1_HW, WALL_R2_HW, WALL_R3_HW, WALL_CA_HW,
        ROOF_R1, ROOF_R2, ROOF_R3, ROOF_CA_HW
    )

    print(f"Lightweight: wall C/A={WALL_CA_LW} kJ/m²K, roof C/A={ROOF_CA_LW} kJ/m²K")
    print(f"Heavyweight: wall C/A={WALL_CA_HW} kJ/m²K, roof C/A={ROOF_CA_HW} kJ/m²K")
    print(f"Total C: LW={C_WALL_LW/1e6:.2f}+{C_ROOF_LW/1e6:.2f} MJ/K, HW={C_WALL_HW/1e6:.2f}+{C_ROOF_HW/1e6:.2f} MJ/K")

    # Run simulations
    print("\nRunning simulations...")
    res_lw: pd.DataFrame = run_rc_hourly(weather, env_lw, air, T_set, vent_ACH, gains)
    res_hw: pd.DataFrame = run_rc_hourly(weather, env_hw, air, T_set, vent_ACH, gains)

    return res_lw, res_hw, weather


def print_results(res_lw: pd.DataFrame, res_hw: pd.DataFrame) -> None:
    """Print heating load and thermal mass statistics."""

    # Heating load stats (kW)
    Q_lw = res_lw['Q_heat_W'].values / 1000
    Q_hw = res_hw['Q_heat_W'].values / 1000

    # Total annual heating (kWh) - sum of Q * dt (15 min = 0.25 hr)
    dt_hours = 0.25
    total_lw = (Q_lw * dt_hours).sum()
    total_hw = (Q_hw * dt_hours).sum()

    print("\nHeating load (kW):")
    print(f"  Lightweight: mean={Q_lw.mean():.3f}, std={Q_lw.std():.3f}")
    print(f"  Heavyweight: mean={Q_hw.mean():.3f}, std={Q_hw.std():.3f}")
    print(f"\nAnnual heating (kWh):")
    print(f"  Lightweight: {total_lw:.1f} kWh")
    print(f"  Heavyweight: {total_hw:.1f} kWh ({(total_hw - total_lw) / total_lw * 100:+.1f}%)")

    print("\nThermal mass temps (mean/std):")
    surfaces = [
        ('Roof', 'T_C_roof'),
        ('North', 'T_C_N'),
        ('South', 'T_C_S'),
        ('East', 'T_C_E'),
        ('West', 'T_C_W'),
    ]
    for name, col in surfaces:
        lw_mean = res_lw[col].mean()
        lw_std = res_lw[col].std()
        hw_mean = res_hw[col].mean()
        hw_std = res_hw[col].std()
        print(f"  {name}: LW {lw_mean:.1f}C (std {lw_std:.2f}), HW {hw_mean:.1f}C (std {hw_std:.2f})")


if __name__ == '__main__':
    os.makedirs('outputs', exist_ok=True)

    res_lw, res_hw, weather = run_simulations()
    print_results(res_lw, res_hw)

    print("\nGenerating plots...")
    plot_glasgow_weather(weather)
    plot_rc_heatup_week(res_lw, res_hw, weather)
    plot_rc_shoulder_week(res_lw, res_hw, weather)
    plot_rc_shoulder_heating(res_lw, res_hw, weather)
    plot_heating_histogram(res_lw, res_hw)
    plot_heating_comparison_histogram(res_lw, res_hw)
    plot_monthly_peak_demand(res_lw, res_hw)

    print("\nDone.")
