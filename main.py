#!/usr/bin/env python3
"""BESTEST Case 600 - Parametric heating load analysis"""

import os
import numpy as np
import pandas as pd

from config import *
from src.building import Plane, AirSide, InternalGains
from src.physics import run_hourly
from src.weather import load_epw_weather
from src.results import (print_table_4, print_table_5, plot_fig2_monthly,
                         plot_fig2_2_breakdown, plot_fig3_pies, plot_fig4_stacked,
                         plot_fig4_2_gains, plot_fig5_winter, plot_fig6_shoulder)


def make_setpoint_array(timestamps, constant=True):
    hrs = pd.Series(timestamps).dt.hour
    if constant:
        return np.full(len(hrs), 21.0)
    return np.where((hrs >= 7) & (hrs < 23), 21.0, 18.0)


def make_vent_array(timestamps, constant=True):
    hrs = pd.Series(timestamps).dt.hour
    if constant:
        return np.full(len(hrs), 0.5)
    return np.where((hrs >= 7) & (hrs < 23), 0.7, 0.3)


def run_scenarios(weather, planes, air, gains):
    scenarios = {
        'S1': (True, True),
        'S2': (False, True),
        'S3': (True, False),
        'S4': (False, False),
    }

    results = {}
    for name, (sp_const, vent_const) in scenarios.items():
        T_int = make_setpoint_array(weather['timestamp'], sp_const)
        vent = make_vent_array(weather['timestamp'], vent_const)
        res = run_hourly(weather, planes, air, T_int, vent_ACH=vent, gains=gains)
        results[name] = res

        kwh = res['Q_heat_W'].sum() / 1000
        print(f"  {name}: {kwh:.0f} kWh ({kwh/FLOOR_AREA:.1f} kWh/m²)")

    return results


if __name__ == '__main__':
    os.makedirs('outputs', exist_ok=True)

    print("Loading weather...")
    weather = load_epw_weather(
        'weather_files/GBR_SCT_Glasgow.AP.031400_TMYx/GBR_SCT_Glasgow.AP.031400_TMYx.epw',
        'weather_files/solarposition_data_Glasgow.csv'
    )
    weather['timestamp'] = pd.to_datetime({
        'year': 2021, 'month': weather['timestamp'].dt.month,
        'day': weather['timestamp'].dt.day, 'hour': weather['timestamp'].dt.hour
    })
    weather = weather.sort_values('timestamp').reset_index(drop=True)

    # setup building
    planes = [
        Plane('Roof', 'opaque', 48.0, 0, 0, ROOF_U, ALPHA, EPSILON),
        Plane('Wall-N', 'opaque', 20.0, 90, 0, WALL_U, ALPHA, EPSILON),
        Plane('Wall-S', 'opaque', 8.0, 90, 180, WALL_U, ALPHA, EPSILON),
        Plane('Wall-E', 'opaque', 15.0, 90, 90, WALL_U, ALPHA, EPSILON),
        Plane('Wall-W', 'opaque', 15.0, 90, 270, WALL_U, ALPHA, EPSILON),
        Plane('Window-S', 'window', 12.0, 90, 180, WINDOW_U, g=SHGC),
    ]
    air = AirSide(BUILDING_VOLUME, VENT_FLOW, HRV_EFF, INFILTRATION_ACH)
    gains = InternalGains(INTERNAL_GAIN_W / 1000)

    print("\nRunning scenarios...")
    results = run_scenarios(weather, planes, air, gains)

    ts = results['S1']['timestamp']
    winter = (ts >= '2021-01-08') & (ts < '2021-01-15')
    shoulder = (ts >= '2021-10-07') & (ts < '2021-10-14')

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
    plot_fig5_winter(results, winter, weather, 'outputs/fig5_winter.png')
    print("  fig5_winter.png")
    plot_fig6_shoulder(results, shoulder, weather, 'outputs/fig6_shoulder.png')
    print("  fig6_shoulder.png")

    print("\nDone.")
