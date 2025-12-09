#!/usr/bin/env python3
"""BESTEST Case 600 - Parametric heating load analysis"""

import os
import numpy as np
import pandas as pd

from config import (
    FLOOR_AREA, BUILDING_VOLUME, VENT_FLOW, HRV_EFF, INFILTRATION_ACH,
    INTERNAL_GAIN_W, ALPHA, EPSILON, SHGC,
    WALL_R, ROOF_R, WINDOW_R,
    AREA_ROOF, AREA_WALL_N, AREA_WALL_S, AREA_WALL_E, AREA_WALL_W, AREA_WINDOW
)
from src.building import Plane, AirSide, InternalGains
from src.physics import run_hourly
from src.weather import load_epw_weather
from src.results import (print_table_4, print_table_5, plot_fig2_monthly,
                         plot_fig2_2_breakdown, plot_fig3_pies, plot_fig4_stacked,
                         plot_fig4_2_gains, plot_fig5_winter, plot_fig6_shoulder)


def setpoint_schedule(timestamps, constant: bool = True) -> np.ndarray:
    """Return hourly setpoint temperatures."""
    hours: np.ndarray = pd.Series(timestamps).dt.hour.values
    if constant:
        return np.full(len(hours), 21.0)
    return np.where((hours >= 7) & (hours < 23), 21.0, 18.0)


def vent_schedule(timestamps, constant: bool = True) -> np.ndarray:
    """Return hourly ventilation rates."""
    hours: np.ndarray = pd.Series(timestamps).dt.hour.values
    if constant:
        return np.full(len(hours), 0.5)
    return np.where((hours >= 7) & (hours < 23), 0.7, 0.3)


def run_scenarios(weather: pd.DataFrame, planes: list, air, gains) -> dict:
    """Run all four scenarios and return results."""
    results = {}

    # S1: constant setpoint, constant ventilation
    T_set_S1: np.ndarray = setpoint_schedule(weather['timestamp'], constant=True)
    vent_S1: np.ndarray = vent_schedule(weather['timestamp'], constant=True)
    results['S1'] = run_hourly(weather, planes, air, T_set_S1, vent_ACH=vent_S1, gains=gains)
    kwh_S1 = results['S1']['Q_heat_W'].sum() / 1000
    print(f"  S1: {kwh_S1:.0f} kWh ({kwh_S1/FLOOR_AREA:.1f} kWh/m²)")

    # S2: variable setpoint, constant ventilation
    T_set_S2: np.ndarray = setpoint_schedule(weather['timestamp'], constant=False)
    vent_S2: np.ndarray = vent_schedule(weather['timestamp'], constant=True)
    results['S2'] = run_hourly(weather, planes, air, T_set_S2, vent_ACH=vent_S2, gains=gains)
    kwh_S2 = results['S2']['Q_heat_W'].sum() / 1000
    print(f"  S2: {kwh_S2:.0f} kWh ({kwh_S2/FLOOR_AREA:.1f} kWh/m²)")

    # S3: constant setpoint, variable ventilation
    T_set_S3: np.ndarray = setpoint_schedule(weather['timestamp'], constant=True)
    vent_S3: np.ndarray = vent_schedule(weather['timestamp'], constant=False)
    results['S3'] = run_hourly(weather, planes, air, T_set_S3, vent_ACH=vent_S3, gains=gains)
    kwh_S3 = results['S3']['Q_heat_W'].sum() / 1000
    print(f"  S3: {kwh_S3:.0f} kWh ({kwh_S3/FLOOR_AREA:.1f} kWh/m²)")

    # S4: variable setpoint, variable ventilation
    T_set_S4: np.ndarray = setpoint_schedule(weather['timestamp'], constant=False)
    vent_S4: np.ndarray = vent_schedule(weather['timestamp'], constant=False)
    results['S4'] = run_hourly(weather, planes, air, T_set_S4, vent_ACH=vent_S4, gains=gains)
    kwh_S4 = results['S4']['Q_heat_W'].sum() / 1000
    print(f"  S4: {kwh_S4:.0f} kWh ({kwh_S4/FLOOR_AREA:.1f} kWh/m²)")

    return results


if __name__ == '__main__':
    os.makedirs('outputs', exist_ok=True)

    # Load weather data
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

    # Building envelope
    roof = Plane('Roof', 'opaque', AREA_ROOF, 0, 0, ROOF_R, ALPHA, EPSILON)
    wall_N = Plane('Wall-N', 'opaque', AREA_WALL_N, 90, 0, WALL_R, ALPHA, EPSILON)
    wall_S = Plane('Wall-S', 'opaque', AREA_WALL_S, 90, 180, WALL_R, ALPHA, EPSILON)
    wall_E = Plane('Wall-E', 'opaque', AREA_WALL_E, 90, 90, WALL_R, ALPHA, EPSILON)
    wall_W = Plane('Wall-W', 'opaque', AREA_WALL_W, 90, 270, WALL_R, ALPHA, EPSILON)
    window_S = Plane('Win-S', 'window', AREA_WINDOW, 90, 180, WINDOW_R, g=SHGC)

    planes = [roof, wall_N, wall_S, wall_E, wall_W, window_S]
    air = AirSide(BUILDING_VOLUME, VENT_FLOW, HRV_EFF, INFILTRATION_ACH)
    gains = InternalGains(INTERNAL_GAIN_W / 1000)

    print("\nRunning scenarios...")
    results: dict = run_scenarios(weather, planes, air, gains)

    # Time masks for weekly analysis
    timestamps = results['S1']['timestamp']
    winter_mask = (timestamps >= '2021-01-08') & (timestamps < '2021-01-15')
    shoulder_mask = (timestamps >= '2021-10-07') & (timestamps < '2021-10-14')

    print_table_4(results)
    print_table_5(results, FLOOR_AREA)

    print("\nGenerating figures...")
    plot_fig2_monthly(results, weather, 'outputs/fig2_monthly.png')
    print("  fig2_monthly.png")
    plot_fig2_2_breakdown(results, weather, 'outputs/fig2_2_breakdown.png')
    print("  fig2_2_breakdown.png")
    plot_fig3_pies(results, 'outputs/fig3_breakdown.png')
    print("  fig3_breakdown.png")
    plot_fig4_stacked(results, 'outputs/fig4_comparison.png')
    print("  fig4_comparison.png")
    plot_fig4_2_gains(results, 'outputs/fig4_2_gains.png')
    print("  fig4_2_gains.png")
    plot_fig5_winter(results, winter_mask, weather, 'outputs/fig5_winter.png')
    print("  fig5_winter.png")
    plot_fig6_shoulder(results, shoulder_mask, weather, 'outputs/fig6_shoulder.png')
    print("  fig6_shoulder.png")

    print("\nDone.")
