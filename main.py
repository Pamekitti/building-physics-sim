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
from visualize import plot_temp_overview, plot_solar_radiation, plot_sun_path, plot_design_days, plot_temp_heatmap
import matplotlib.pyplot as plt


def main():
    # Load weather
    weather = load_epw_weather('weather_files/SWE_ST_Stockholm.Arlanda.AP.024600_TMYx.2004-2018/SWE_ST_Stockholm.Arlanda.AP.024600_TMYx.2004-2018.epw')

    # Normalize all to same year for continuous plotting
    weather['timestamp'] = pd.to_datetime({
        'year': 2018,
        'month': weather['timestamp'].dt.month,
        'day': weather['timestamp'].dt.day,
        'hour': weather['timestamp'].dt.hour
    })

    # Sort by timestamp to fix plotting
    weather = weather.sort_values('timestamp').reset_index(drop=True)

    # Quick EDA
    print("Weather Data Summary:")
    print(f"  Temperature range: {weather['T_out_C'].min():.1f} to {weather['T_out_C'].max():.1f}°C")
    print(f"  Ground temp range: {weather['T_ground_C'].min():.1f} to {weather['T_ground_C'].max():.1f}°C")
    print(f"  Max solar (direct): {weather['I_dir_Wm2'].max():.0f} W/m²")
    print(f"  Max solar (diffuse): {weather['I_dif_Wm2'].max():.0f} W/m²")
    print("")

    # Design conditions
    temps = weather['T_out_C']
    heat_design_temp = np.percentile(temps, 0.4)
    cool_design_temp = np.percentile(temps, 99.6)

    # Find design days
    weather['Date'] = weather['timestamp'].dt.date
    daily_min = weather.groupby('Date')['T_out_C'].min().reset_index()
    daily_max = weather.groupby('Date')['T_out_C'].max().reset_index()
    heat_day = daily_min.iloc[daily_min['T_out_C'].idxmin()]['Date']
    cool_day = daily_max.iloc[daily_max['T_out_C'].idxmax()]['Date']

    heat_weather = weather[weather['Date'] == heat_day].copy()
    cool_weather = weather[weather['Date'] == cool_day].copy()

    # Design day details
    heat_temp_min = heat_weather['T_out_C'].min()
    heat_temp_max = heat_weather['T_out_C'].max()
    heat_temp_avg = heat_weather['T_out_C'].mean()
    heat_solar_max = heat_weather['I_dir_Wm2'].max()

    cool_temp_min = cool_weather['T_out_C'].min()
    cool_temp_max = cool_weather['T_out_C'].max()
    cool_temp_avg = cool_weather['T_out_C'].mean()
    cool_solar_max = cool_weather['I_dir_Wm2'].max()

    # Generate plots
    os.makedirs('plots', exist_ok=True)
    print("Generating weather analysis plots...")

    fig1 = plot_temp_overview(weather)
    fig1.savefig('plots/temperature.png', dpi=150, bbox_inches='tight')

    fig2 = plot_solar_radiation(weather)
    fig2.savefig('plots/solar.png', dpi=150, bbox_inches='tight')

    fig3 = plot_sun_path(weather)
    fig3.savefig('plots/solar_elevation.png', dpi=150, bbox_inches='tight')

    fig4 = plot_temp_heatmap(weather)
    fig4.savefig('plots/temp_heatmap.png', dpi=150, bbox_inches='tight')

    fig5 = plot_design_days(heat_weather, cool_weather)
    fig5.savefig('plots/design_days.png', dpi=150, bbox_inches='tight')

    plt.close('all')
    print("Saved plots to plots/ folder")
    print("")

    # Building envelope
    planes = [
        # Walls
        Plane('WW-N', 'opaque', area_m2=372.8, tilt_deg=90, azimuth_deg=7, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('WW-S', 'opaque', area_m2=357.4, tilt_deg=90, azimuth_deg=187, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('WW-W', 'opaque', area_m2=139.9, tilt_deg=90, azimuth_deg=277, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('C-NE', 'opaque', area_m2=80.6, tilt_deg=90, azimuth_deg=116, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('C-SW', 'opaque', area_m2=80.6, tilt_deg=90, azimuth_deg=296, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('C-NW', 'opaque', area_m2=128.7, tilt_deg=90, azimuth_deg=206, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('SW-E', 'opaque', area_m2=372.8, tilt_deg=90, azimuth_deg=77, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('SW-W', 'opaque', area_m2=357.4, tilt_deg=90, azimuth_deg=257, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        Plane('SW-S', 'opaque', area_m2=139.9, tilt_deg=90, azimuth_deg=167, U=AG_WALL_U, alpha=WALL_ALPHA, epsilon=EPSILON),
        # Roofs
        Plane('WW-RN', 'opaque', area_m2=288.0, tilt_deg=25, azimuth_deg=7, U=AG_ROOF_U, alpha=ROOF_ALPHA, epsilon=EPSILON),
        Plane('WW-RS', 'opaque', area_m2=283.8, tilt_deg=25, azimuth_deg=187, U=AG_ROOF_U, alpha=ROOF_ALPHA, epsilon=EPSILON),
        Plane('C-RNE', 'opaque', area_m2=69.4, tilt_deg=25, azimuth_deg=116, U=AG_ROOF_U, alpha=ROOF_ALPHA, epsilon=EPSILON),
        Plane('C-RSW', 'opaque', area_m2=69.4, tilt_deg=25, azimuth_deg=296, U=AG_ROOF_U, alpha=ROOF_ALPHA, epsilon=EPSILON),
        Plane('SW-RE', 'opaque', area_m2=288.0, tilt_deg=25, azimuth_deg=77, U=AG_ROOF_U, alpha=ROOF_ALPHA, epsilon=EPSILON),
        Plane('SW-RW', 'opaque', area_m2=283.8, tilt_deg=25, azimuth_deg=257, U=AG_ROOF_U, alpha=ROOF_ALPHA, epsilon=EPSILON),
        # Windows
        Plane('WW-N-Win', 'window', area_m2=141.2, tilt_deg=90, azimuth_deg=7, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('WW-S-Win', 'window', area_m2=141.2, tilt_deg=90, azimuth_deg=187, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('WW-W-Win', 'window', area_m2=13.6, tilt_deg=90, azimuth_deg=277, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('C-NE-Win', 'window', area_m2=24.8, tilt_deg=90, azimuth_deg=116, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('C-SW-Win', 'window', area_m2=24.8, tilt_deg=90, azimuth_deg=296, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('C-NW-Win', 'window', area_m2=24.8, tilt_deg=90, azimuth_deg=206, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('SW-E-Win', 'window', area_m2=141.2, tilt_deg=90, azimuth_deg=77, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('SW-W-Win', 'window', area_m2=141.2, tilt_deg=90, azimuth_deg=257, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        Plane('SW-S-Win', 'window', area_m2=13.6, tilt_deg=90, azimuth_deg=167, U=WINDOW_U, g=WINDOW_G, F_sh=WINDOW_F_SH),
        # Underground
        Plane('UG-Wall', 'opaque', area_m2=PERIMETER * UG_WALL_HEIGHT, tilt_deg=90, azimuth_deg=0,
              U=UG_WALL_U, alpha=0.0, epsilon=EPSILON, ground_contact=True),
        Plane('Floor', 'opaque', area_m2=FLOOR_AREA, tilt_deg=0, azimuth_deg=0,
              U=UG_FLOOR_U, alpha=0.0, epsilon=EPSILON, ground_contact=True),
    ]

    air = AirSide(V_zone_m3=BUILDING_VOLUME, Vdot_vent_m3s=VENT_FLOW,
                  eta_HRV=HRV_EFF, ACH_infiltration_h=INFILTRATION_ACH)

    # Internal gains for cooling only
    gains_cooling = InternalGains(Q_equip_kW=EQUIP_GAIN, Q_occ_kW=OCC_GAIN, Q_light_kW=LIGHT_GAIN)
    gains_heating = None  # No internal gains for heating design (conservative)

    # Kitchen schedule
    kitchen_heat = pd.Series([False] * 24)  # No kitchen for heating design

    kitchen_cool = pd.Series([False] * 24)
    kitchen_cool.iloc[7:9] = True
    kitchen_cool.iloc[12:14] = True
    kitchen_cool.iloc[18:20] = True

    # Run simulations
    heat_res = run_hourly(heat_weather, planes, air, T_HEAT, T_COOL, gains_heating, 0.0, kitchen_heat)
    cool_res = run_hourly(cool_weather, planes, air, T_HEAT, T_COOL, gains_cooling, KITCHEN_GAIN, kitchen_cool)

    # Peak loads
    peak_heat = heat_res.iloc[heat_res['Q_heat_W'].idxmax()]
    peak_cool = cool_res.iloc[cool_res['Q_cool_W'].idxmax()]

    # Summary stats
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
    print(f"Design Conditions:")
    print(f"  Heating Design Temp (0.4%): {heat_design_temp:.1f}°C")
    print(f"  Cooling Design Temp (99.6%): {cool_design_temp:.1f}°C")
    print(f"")
    print(f"Heating Design Day ({heat_day}):")
    print(f"  Temperature: Min {heat_temp_min:.1f}°C, Max {heat_temp_max:.1f}°C, Avg {heat_temp_avg:.1f}°C")
    print(f"  Max Solar (Direct): {heat_solar_max:.0f} W/m²")
    print(f"  Peak Heating Load: {peak_heat['Q_heat_W']/1000:.1f} kW")
    print(f"")
    print(f"Cooling Design Day ({cool_day}):")
    print(f"  Temperature: Min {cool_temp_min:.1f}°C, Max {cool_temp_max:.1f}°C, Avg {cool_temp_avg:.1f}°C")
    print(f"  Max Solar (Direct): {cool_solar_max:.0f} W/m²")
    print(f"  Peak Cooling Load: {peak_cool['Q_cool_W']/1000:.1f} kW")

    return heat_res, cool_res


if __name__ == '__main__':
    heat_res, cool_res = main()
