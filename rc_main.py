#!/usr/bin/env python3
# Compare lightweight vs heavyweight buildings with RC model

import os
import pandas as pd

from config import (
    FLOOR_AREA, BUILDING_VOLUME,
    AREA_ROOF, AREA_WALL_N, AREA_WALL_S, AREA_WALL_E, AREA_WALL_W, AREA_WINDOW,
    WALL_R, ROOF_R, WINDOW_R,
    ALPHA, SHGC, INFILTRATION_ACH, INTERNAL_GAIN_W
)
from config_heavyweight import (
    WALL_R_HW, ROOF_R_HW,
    C_WALL_HW, C_ROOF_HW,
    C_WALL_LW, C_ROOF_LW,
    TOTAL_WALL_AREA
)
from src.building import AirSide, InternalGains
from src.weather import load_epw_weather
from src.rc_model import run_rc_hourly
from src.rc_plots import plot_rc_comparison


def build_envelope(wall_R: float, roof_R: float, C_wall_total: float, C_roof: float) -> dict:
    """Build envelope parameters for RC model."""

    # Split R equally between indoor and outdoor sides
    r1_wall = wall_R / 2
    r2_wall = wall_R / 2
    r1_roof = roof_R / 2
    r2_roof = roof_R / 2

    # Distribute wall capacitance by area
    C_N = C_wall_total * (AREA_WALL_N / TOTAL_WALL_AREA)
    C_S = C_wall_total * (AREA_WALL_S / TOTAL_WALL_AREA)
    C_E = C_wall_total * (AREA_WALL_E / TOTAL_WALL_AREA)
    C_W = C_wall_total * (AREA_WALL_W / TOTAL_WALL_AREA)

    # Roof
    roof = {
        'R1': r1_roof / AREA_ROOF,
        'R2': r2_roof / AREA_ROOF,
        'C': C_roof,
        'alpha': ALPHA,
    }

    # Walls
    wall_N = {'R1': r1_wall / AREA_WALL_N, 'R2': r2_wall / AREA_WALL_N, 'C': C_N, 'alpha': ALPHA}
    wall_S = {'R1': r1_wall / AREA_WALL_S, 'R2': r2_wall / AREA_WALL_S, 'C': C_S, 'alpha': ALPHA}
    wall_E = {'R1': r1_wall / AREA_WALL_E, 'R2': r2_wall / AREA_WALL_E, 'C': C_E, 'alpha': ALPHA}
    wall_W = {'R1': r1_wall / AREA_WALL_W, 'R2': r2_wall / AREA_WALL_W, 'C': C_W, 'alpha': ALPHA}

    # Windows
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

    # Building parameters
    air = AirSide(BUILDING_VOLUME, 0.0, 0.0, INFILTRATION_ACH)
    gains = InternalGains(INTERNAL_GAIN_W / 1000)
    T_set = 20.0
    vent_ACH = 0.0

    # Build envelopes
    env_lw: dict = build_envelope(WALL_R, ROOF_R, C_WALL_LW, C_ROOF_LW)
    env_hw: dict = build_envelope(WALL_R_HW, ROOF_R_HW, C_WALL_HW, C_ROOF_HW)

    print(f"Lightweight C: {C_WALL_LW/1e6:.2f} MJ/K (walls), {C_ROOF_LW/1e6:.2f} MJ/K (roof)")
    print(f"Heavyweight C: {C_WALL_HW/1e6:.2f} MJ/K (walls), {C_ROOF_HW/1e6:.2f} MJ/K (roof)")

    # Run simulations
    print("\nRunning simulations...")
    res_lw: pd.DataFrame = run_rc_hourly(weather, env_lw, air, T_set, vent_ACH, gains)
    res_hw: pd.DataFrame = run_rc_hourly(weather, env_hw, air, T_set, vent_ACH, gains)

    return res_lw, res_hw, T_set


def print_results(res_lw: pd.DataFrame, res_hw: pd.DataFrame) -> None:
    """Print annual heating and thermal mass statistics."""

    kwh_lw = res_lw['Q_heat_W'].sum() / 1000
    kwh_hw = res_hw['Q_heat_W'].sum() / 1000

    print("\nAnnual heating:")
    print(f"  Lightweight: {kwh_lw:.0f} kWh ({kwh_lw/FLOOR_AREA:.1f} kWh/m2)")
    print(f"  Heavyweight: {kwh_hw:.0f} kWh ({kwh_hw/FLOOR_AREA:.1f} kWh/m2)")
    print(f"  Difference: {kwh_hw - kwh_lw:.0f} kWh ({(kwh_hw/kwh_lw - 1)*100:.1f}%)")

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

    res_lw, res_hw, T_set = run_simulations()
    print_results(res_lw, res_hw)
    plot_rc_comparison(res_lw, res_hw, T_set)
