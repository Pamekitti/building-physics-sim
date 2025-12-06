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
from src.sensitivity import (run_sensitivity, calc_sensitivity_table,
                             print_table_7, plot_fig7_scatter, plot_fig8_ranking)


def setpoint_schedule(timestamps, constant=True):
    hrs = pd.Series(timestamps).dt.hour
    if constant:
        return np.full(len(hrs), 21.0)
    return np.where((hrs >= 7) & (hrs < 23), 21.0, 18.0)


def vent_schedule(timestamps, constant=True):
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
        T_set = setpoint_schedule(weather['timestamp'], sp_const)
        vent = vent_schedule(weather['timestamp'], vent_const)
        res = run_hourly(weather, planes, air, T_set, vent_ACH=vent, gains=gains)
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
        'year': 2021,
        'month': weather['timestamp'].dt.month,
        'day': weather['timestamp'].dt.day,
        'hour': weather['timestamp'].dt.hour
    })
    weather = weather.sort_values('timestamp').reset_index(drop=True)

    # building setup
    planes = [
        Plane('Roof',   'opaque', AREA_ROOF,   0,  0,   ROOF_R, ALPHA, EPSILON),
        Plane('Wall-N', 'opaque', AREA_WALL_N, 90, 0,   WALL_R, ALPHA, EPSILON),
        Plane('Wall-S', 'opaque', AREA_WALL_S, 90, 180, WALL_R, ALPHA, EPSILON),
        Plane('Wall-E', 'opaque', AREA_WALL_E, 90, 90,  WALL_R, ALPHA, EPSILON),
        Plane('Wall-W', 'opaque', AREA_WALL_W, 90, 270, WALL_R, ALPHA, EPSILON),
        Plane('Win-S',  'window', AREA_WINDOW, 90, 180, WINDOW_R, g=SHGC),
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

    # sensitivity analysis
    print("\nRunning sensitivity analysis...")
    winter_mask = (weather['timestamp'] >= '2021-01-08') & (weather['timestamp'] < '2021-01-15')
    shoulder_mask = (weather['timestamp'] >= '2021-10-07') & (weather['timestamp'] < '2021-10-14')

    sens_df = run_sensitivity(weather, winter_mask, shoulder_mask)
    sens_table = calc_sensitivity_table(sens_df)
    print_table_7(sens_table)

    print("\nGenerating sensitivity figures...")
    plot_fig7_scatter(sens_df, 'outputs/fig7_sensitivity.png')
    print("  fig7_sensitivity.png")
    plot_fig8_ranking(sens_table, 'outputs/fig8_ranking.png')
    print("  fig8_ranking.png")

    print("\nDone.")
