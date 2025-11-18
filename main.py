#!/usr/bin/env python3

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import os
from config import *
from building import Plane, AirSide, InternalGains
from physics import run_hourly
from weather import load_epw_weather
from visualize import plot_temp_overview, plot_solar_radiation, plot_sun_path, plot_temp_heatmap, plot_hourly_stacked_bar, plot_heat_distribution
import matplotlib.pyplot as plt

def main():
    weather = load_epw_weather('weather_files/SWE_ST_Stockholm.Arlanda.AP.024600_TMYx.2004-2018/SWE_ST_Stockholm.Arlanda.AP.024600_TMYx.2004-2018.epw')

    weather['timestamp'] = pd.to_datetime({
        'year': 2018,
        'month': weather['timestamp'].dt.month,
        'day': weather['timestamp'].dt.day,
        'hour': weather['timestamp'].dt.hour
    })
    weather = weather.sort_values('timestamp').reset_index(drop=True)

    print("Weather Data Summary:")
    print(f"  Temperature range: {weather['T_out_C'].min():.1f} to {weather['T_out_C'].max():.1f}°C")
    print(f"  Ground temp range: {weather['T_ground_C'].min():.1f} to {weather['T_ground_C'].max():.1f}°C")
    print(f"  Max solar (direct): {weather['I_dir_Wm2'].max():.0f} W/m²")
    print(f"  Max solar (diffuse): {weather['I_dif_Wm2'].max():.0f} W/m²")
    print("")

    # find coldest day
    weather['Date'] = weather['timestamp'].dt.date
    daily_min = weather.groupby('Date')['T_out_C'].min().reset_index()
    design_day = daily_min.iloc[daily_min['T_out_C'].idxmin()]['Date']
    design_weather = weather[weather['Date'] == design_day].copy()

    tmin = design_weather['T_out_C'].min()
    tmax = design_weather['T_out_C'].max()
    tavg = design_weather['T_out_C'].mean()
    solar_max = design_weather['I_dir_Wm2'].max()

    os.makedirs('plots', exist_ok=True)
    print("Generating weather plots...")

    fig1 = plot_temp_overview(weather)
    fig1.savefig('plots/temperature.png', dpi=150, bbox_inches='tight')
    fig2 = plot_solar_radiation(weather)
    fig2.savefig('plots/solar.png', dpi=150, bbox_inches='tight')
    fig3 = plot_sun_path(weather)
    fig3.savefig('plots/solar_elevation.png', dpi=150, bbox_inches='tight')
    fig4 = plot_temp_heatmap(weather)
    fig4.savefig('plots/temp_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close('all')
    print("Saved weather plots")
    print("")

    planes = [
        Plane('WW-N', 'opaque', area_m2=372.8, tilt_deg=90, azimuth_deg=7, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('WW-S', 'opaque', area_m2=357.4, tilt_deg=90, azimuth_deg=187, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('WW-W', 'opaque', area_m2=139.9, tilt_deg=90, azimuth_deg=277, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('C-NE', 'opaque', area_m2=80.6, tilt_deg=90, azimuth_deg=116, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('C-SW', 'opaque', area_m2=80.6, tilt_deg=90, azimuth_deg=296, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('C-NW', 'opaque', area_m2=128.7, tilt_deg=90, azimuth_deg=206, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('SW-E', 'opaque', area_m2=372.8, tilt_deg=90, azimuth_deg=77, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('SW-W', 'opaque', area_m2=357.4, tilt_deg=90, azimuth_deg=257, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('SW-S', 'opaque', area_m2=139.9, tilt_deg=90, azimuth_deg=167, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('WW-RN', 'opaque', area_m2=288.0, tilt_deg=25, azimuth_deg=7, U=AG_ROOF_U, alpha=ROOF_ALPHA, epsilon=EPSILON),
        Plane('WW-RS', 'opaque', area_m2=283.8, tilt_deg=25, azimuth_deg=187, U=AG_ROOF_U, alpha=ROOF_ALPHA, epsilon=EPSILON),
        Plane('C-RNE', 'opaque', area_m2=69.4, tilt_deg=25, azimuth_deg=116, U=AG_ROOF_U, alpha=ROOF_ALPHA, epsilon=EPSILON),
        Plane('C-RSW', 'opaque', area_m2=69.4, tilt_deg=25, azimuth_deg=296, U=AG_ROOF_U, alpha=ROOF_ALPHA, epsilon=EPSILON),
        Plane('SW-RE', 'opaque', area_m2=288.0, tilt_deg=25, azimuth_deg=77, U=AG_ROOF_U, alpha=ROOF_ALPHA, epsilon=EPSILON),
        Plane('SW-RW', 'opaque', area_m2=283.8, tilt_deg=25, azimuth_deg=257, U=AG_ROOF_U, alpha=ROOF_ALPHA, epsilon=EPSILON),
        Plane('WW-N-Win', 'window', area_m2=141.2, tilt_deg=90, azimuth_deg=7, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('WW-S-Win', 'window', area_m2=141.2, tilt_deg=90, azimuth_deg=187, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('WW-W-Win', 'window', area_m2=13.6, tilt_deg=90, azimuth_deg=277, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('C-NE-Win', 'window', area_m2=24.8, tilt_deg=90, azimuth_deg=116, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('C-SW-Win', 'window', area_m2=24.8, tilt_deg=90, azimuth_deg=296, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('C-NW-Win', 'window', area_m2=24.8, tilt_deg=90, azimuth_deg=206, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('SW-E-Win', 'window', area_m2=141.2, tilt_deg=90, azimuth_deg=77, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('SW-W-Win', 'window', area_m2=141.2, tilt_deg=90, azimuth_deg=257, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('SW-S-Win', 'window', area_m2=13.6, tilt_deg=90, azimuth_deg=167, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('UG-Wall', 'opaque', area_m2=PERIMETER * UG_WALL_HEIGHT, tilt_deg=90, azimuth_deg=0,
              U=UG_WALL_U, alpha=0.0, epsilon=EPSILON, ground_contact=True),
        Plane('Floor', 'opaque', area_m2=FLOOR_AREA, tilt_deg=0, azimuth_deg=0,
              U=UG_FLOOR_U, alpha=0.0, epsilon=EPSILON, ground_contact=True),
    ]

    air = AirSide(V_zone_m3=BUILDING_VOLUME, Vdot_vent_m3s=VENT_FLOW,
                  eta_HRV=HRV_EFF, ACH_infiltration_h=INFILTRATION_ACH)

    kitchen = pd.Series([False] * 24)

    results = run_hourly(design_weather, planes, air, T_HEAT, T_COOL, None, 0.0, kitchen)
    peak_load = results['Q_heat_W'].max() / 1000

    total_UA = sum(p.U * p.area_m2 for p in planes)
    wall_area = sum(p.area_m2 for p in planes if p.is_opaque() and p.tilt_deg == 90 and not p.ground_contact)
    roof_area = sum(p.area_m2 for p in planes if p.is_opaque() and p.tilt_deg == 25)
    window_area = sum(p.area_m2 for p in planes if p.is_window())
    floor_area = sum(p.area_m2 for p in planes if p.is_opaque() and p.tilt_deg == 0)

    print(f"Building Envelope:")
    print(f"  Wall area: {wall_area:.1f} m²")
    print(f"  Roof area: {roof_area:.1f} m²")
    print(f"  Window area: {window_area:.1f} m²")
    print(f"  Floor area: {floor_area:.1f} m²")
    print(f"  Total UA: {total_UA:.1f} W/K")
    print(f"")
    print(f"Design Day ({design_day}):")
    print(f"  Temperature: Min {tmin:.1f}°C, Max {tmax:.1f}°C, Avg {tavg:.1f}°C")
    print(f"  Max Solar: {solar_max:.0f} W/m²")
    print(f"  Peak Heating Load: {peak_load:.1f} kW")
    print(f"")

    # generate hourly heat balance plots
    print("Generating design day analysis...")
    # Calculate yearly max solar elevation
    yearly_solar_elev_max = (90 - weather['theta_s_deg']).max()
    fig_bar = plot_hourly_stacked_bar(results, solar_elev_max_year=yearly_solar_elev_max)
    fig_bar.savefig('plots/hourly_stacked_bar.png', dpi=150, bbox_inches='tight')
    fig_pie = plot_heat_distribution(results)
    fig_pie.savefig('plots/heat_distribution.png', dpi=150, bbox_inches='tight')
    plt.close('all')
    print("Saved design day analysis")

    return results


if __name__ == '__main__':
    results = main()
