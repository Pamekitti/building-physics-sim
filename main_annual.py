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
import matplotlib.pyplot as plt


def plot_annual_energy(results):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Monthly energy consumption
    results['month'] = results['timestamp'].dt.month
    monthly = results.groupby('month').agg({
        'Q_heat_W': lambda x: x.sum() / 1000,  # kWh
        'Q_cool_W': lambda x: x.sum() / 1000   # kWh
    })

    months = range(1, 13)
    x = np.arange(len(months))
    width = 0.35

    axes[0, 0].bar(x - width/2, monthly['Q_heat_W'], width,
                   color='#3498DB', alpha=0.8, label='Heating')
    axes[0, 0].bar(x + width/2, monthly['Q_cool_W'], width,
                   color='#E74C3C', alpha=0.8, label='Cooling')
    axes[0, 0].set_xlabel('Month')
    axes[0, 0].set_ylabel('Energy (kWh)')
    axes[0, 0].set_title('Monthly Energy Consumption')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(months)
    axes[0, 0].legend(frameon=False)
    axes[0, 0].grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.5)
    axes[0, 0].spines['top'].set_visible(False)
    axes[0, 0].spines['right'].set_visible(False)

    # Annual totals
    total_heat = results['Q_heat_W'].sum() / 1000
    total_cool = results['Q_cool_W'].sum() / 1000
    total_energy = total_heat + total_cool

    categories = ['Heating', 'Cooling', 'Total']
    values = [total_heat, total_cool, total_energy]
    colors = ['#3498DB', '#E74C3C', '#34495E']

    axes[0, 1].bar(categories, values, color=colors, alpha=0.8)
    axes[0, 1].set_ylabel('Energy (kWh/year)')
    axes[0, 1].set_title('Annual Energy Consumption')
    axes[0, 1].grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.5)
    axes[0, 1].spines['top'].set_visible(False)
    axes[0, 1].spines['right'].set_visible(False)

    # Add values on bars
    for i, v in enumerate(values):
        axes[0, 1].text(i, v + max(values)*0.02, f'{v:.0f}',
                       ha='center', va='bottom', fontsize=10)

    # Energy intensity
    from config import ATEMP
    heat_intensity = total_heat / ATEMP
    cool_intensity = total_cool / ATEMP
    total_intensity = total_energy / ATEMP

    categories_int = ['Heating', 'Cooling', 'Total']
    values_int = [heat_intensity, cool_intensity, total_intensity]

    axes[1, 0].bar(categories_int, values_int, color=colors, alpha=0.8)
    axes[1, 0].set_ylabel('Energy Intensity (kWh/m²·year)')
    axes[1, 0].set_title('Annual Energy Intensity')
    axes[1, 0].grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.5)
    axes[1, 0].spines['top'].set_visible(False)
    axes[1, 0].spines['right'].set_visible(False)

    # Add values on bars
    for i, v in enumerate(values_int):
        axes[1, 0].text(i, v + max(values_int)*0.02, f'{v:.1f}',
                       ha='center', va='bottom', fontsize=10)

    # Load duration curve
    sorted_heat = np.sort(results['Q_heat_W'].values / 1000)[::-1]
    sorted_cool = np.sort(results['Q_cool_W'].values / 1000)[::-1]
    hours = np.arange(len(sorted_heat))

    axes[1, 1].plot(hours, sorted_heat, color='#3498DB', linewidth=1.5,
                   alpha=0.8, label='Heating')
    axes[1, 1].plot(hours, sorted_cool, color='#E74C3C', linewidth=1.5,
                   alpha=0.8, label='Cooling')
    axes[1, 1].set_xlabel('Hours')
    axes[1, 1].set_ylabel('Load (kW)')
    axes[1, 1].set_title('Load Duration Curve')
    axes[1, 1].legend(frameon=False)
    axes[1, 1].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[1, 1].spines['top'].set_visible(False)
    axes[1, 1].spines['right'].set_visible(False)

    plt.tight_layout()
    return fig


def plot_load_breakdown(results):
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))

    # Heating components
    axes[0].plot(results['timestamp'], results['Q_trans_h_W']/1000,
                color='#3498DB', linewidth=0.8, alpha=0.6, label='Transmission')
    axes[0].plot(results['timestamp'], results['Q_air_h_W']/1000,
                color='#E67E22', linewidth=0.8, alpha=0.6, label='Ventilation')
    axes[0].plot(results['timestamp'], results['Q_heat_W']/1000,
                color='#2C3E50', linewidth=1.2, label='Total Heating')
    axes[0].set_ylabel('Heating Load (kW)')
    axes[0].set_title('Heating Load Components')
    axes[0].legend(frameon=False)
    axes[0].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)

    # Cooling components
    axes[1].plot(results['timestamp'], results['Q_trans_c_W']/1000,
                color='#E74C3C', linewidth=0.8, alpha=0.6, label='Transmission')
    axes[1].plot(results['timestamp'], results['Q_air_c_W']/1000,
                color='#E67E22', linewidth=0.8, alpha=0.6, label='Ventilation')
    axes[1].plot(results['timestamp'], results['Q_solar_W']/1000,
                color='#F39C12', linewidth=0.8, alpha=0.6, label='Solar')
    axes[1].plot(results['timestamp'], results['Q_int_W']/1000,
                color='#9B59B6', linewidth=0.8, alpha=0.6, label='Internal')
    axes[1].plot(results['timestamp'], results['Q_cool_W']/1000,
                color='#2C3E50', linewidth=1.2, label='Total Cooling')
    axes[1].set_xlabel('Date')
    axes[1].set_ylabel('Cooling Load (kW)')
    axes[1].set_title('Cooling Load Components')
    axes[1].legend(frameon=False)
    axes[1].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)

    plt.tight_layout()
    return fig


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

    # Sort by timestamp
    weather = weather.sort_values('timestamp').reset_index(drop=True)

    print("Annual Energy Simulation")
    print("=" * 50)
    print(f"Total hours: {len(weather)}")
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

    # NO internal gains for heating (conservative)
    # This gives worst-case heating load without internal heat offsets
    gains_none = None

    # No kitchen schedule needed (0 gains)
    kitchen_schedule = pd.Series([False] * len(weather))

    print("Running annual simulation...")
    print("(No internal gains - conservative heating calculation)")
    results = run_hourly(weather, planes, air, T_HEAT, T_COOL, gains_none, 0.0, kitchen_schedule)
    print("Simulation complete!")
    print("")

    # Calculate annual energy
    total_heat_kWh = results['Q_heat_W'].sum() / 1000
    total_cool_kWh = results['Q_cool_W'].sum() / 1000
    total_energy_kWh = total_heat_kWh + total_cool_kWh

    # Calculate energy intensity
    heat_intensity = total_heat_kWh / ATEMP
    cool_intensity = total_cool_kWh / ATEMP
    total_intensity = total_energy_kWh / ATEMP

    # Peak loads
    peak_heat_kW = results['Q_heat_W'].max() / 1000
    peak_cool_kW = results['Q_cool_W'].max() / 1000

    # Print results
    print("Annual Energy Consumption:")
    print(f"  Heating: {total_heat_kWh:,.0f} kWh/year")
    print(f"  Cooling: {total_cool_kWh:,.0f} kWh/year")
    print(f"  Total: {total_energy_kWh:,.0f} kWh/year")
    print("")
    print("Energy Intensity:")
    print(f"  Heating: {heat_intensity:.1f} kWh/m²·year")
    print(f"  Cooling: {cool_intensity:.1f} kWh/m²·year")
    print(f"  Total: {total_intensity:.1f} kWh/m²·year")
    print("")
    print("Peak Loads:")
    print(f"  Heating: {peak_heat_kW:.1f} kW")
    print(f"  Cooling: {peak_cool_kW:.1f} kW")
    print("")

    # Generate plots
    os.makedirs('plots', exist_ok=True)
    print("Generating annual energy plots...")

    fig1 = plot_annual_energy(results)
    fig1.savefig('plots/annual_energy.png', dpi=150, bbox_inches='tight')

    fig2 = plot_load_breakdown(results)
    fig2.savefig('plots/load_breakdown.png', dpi=150, bbox_inches='tight')

    plt.close('all')
    print("Saved plots to plots/ folder")

    return results


if __name__ == '__main__':
    results = main()
