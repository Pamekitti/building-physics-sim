#!/usr/bin/env python3
"""Sensitivity analysis for BESTEST Case 600 building."""

import os
import pandas as pd

from src.weather import load_epw_weather
from src.sensitivity import (run_sensitivity, calc_sensitivity_table,
                             print_table_7, plot_fig7_scatter, plot_fig8_ranking)


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

    # Time masks for weekly analysis
    winter_mask = (weather['timestamp'] >= '2021-01-08') & (weather['timestamp'] < '2021-01-15')
    shoulder_mask = (weather['timestamp'] >= '2021-10-07') & (weather['timestamp'] < '2021-10-14')

    # Run sensitivity analysis
    print("\nRunning sensitivity analysis...")
    sens_df: pd.DataFrame = run_sensitivity(weather, winter_mask, shoulder_mask)
    sens_table: pd.DataFrame = calc_sensitivity_table(sens_df)
    print_table_7(sens_table)

    # Generate figures
    print("\nGenerating sensitivity figures...")
    plot_fig7_scatter(sens_df, 'outputs/fig7_sensitivity.png')
    print("  fig7_sensitivity.png")
    plot_fig8_ranking(sens_table, 'outputs/fig8_ranking.png')
    print("  fig8_ranking.png")

    print("\nDone.")
