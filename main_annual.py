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
from visualize import plot_heat_distribution_4pies, plot_heat_distribution_detailed
import matplotlib.pyplot as plt


def plot_energy(results):
    """Annual heating energy analysis (heating focus only)"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    results['month'] = results['timestamp'].dt.month
    monthly = results.groupby('month').agg({
        'Q_heat_W': lambda x: x.sum() / 1000
    })

    months = range(1, 13)
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    x = np.arange(len(months))

    axes[0, 0].bar(x, monthly['Q_heat_W'], color='#3498DB', alpha=0.8)
    axes[0, 0].set_xlabel('Month')
    axes[0, 0].set_ylabel('Energy (kWh)')
    axes[0, 0].set_title('Monthly Heating Energy')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(month_names)
    axes[0, 0].grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.5)
    axes[0, 0].spines['top'].set_visible(False)
    axes[0, 0].spines['right'].set_visible(False)

    total_heat = results['Q_heat_W'].sum() / 1000
    heat_int = total_heat / ATEMP

    # Annual total
    axes[0, 1].bar(['Annual\nHeating'], [total_heat], color='#3498DB', alpha=0.8, width=0.5)
    axes[0, 1].set_ylabel('Energy (kWh/year)')
    axes[0, 1].set_title('Annual Heating Energy')
    axes[0, 1].grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.5)
    axes[0, 1].spines['top'].set_visible(False)
    axes[0, 1].spines['right'].set_visible(False)
    axes[0, 1].text(0, total_heat + total_heat*0.02, f'{total_heat:,.0f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Energy intensity
    axes[1, 0].bar(['Heating\nIntensity'], [heat_int], color='#3498DB', alpha=0.8, width=0.5)
    axes[1, 0].set_ylabel('Energy Intensity (kWh/m²·year)')
    axes[1, 0].set_title(f'Annual Heating Intensity ({ATEMP:.0f} m²)')
    axes[1, 0].grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.5)
    axes[1, 0].spines['top'].set_visible(False)
    axes[1, 0].spines['right'].set_visible(False)
    axes[1, 0].text(0, heat_int + heat_int*0.02, f'{heat_int:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Load duration curve
    sorted_heat = np.sort(results['Q_heat_W'].values / 1000)[::-1]
    hours = np.arange(len(sorted_heat))

    axes[1, 1].plot(hours, sorted_heat, color='#3498DB', linewidth=1.5, alpha=0.8)
    axes[1, 1].set_xlabel('Hours')
    axes[1, 1].set_ylabel('Heating Load (kW)')
    axes[1, 1].set_title('Heating Load Duration Curve')
    axes[1, 1].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[1, 1].spines['top'].set_visible(False)
    axes[1, 1].spines['right'].set_visible(False)

    plt.tight_layout()
    return fig


def plot_breakdown(results):
    """Heating load components breakdown (heating focus only)"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 6))

    ax.plot(results['timestamp'], abs(results['Q_trans_h_W'])/1000, color='#1A5490', linewidth=0.8, alpha=0.7, label='Transmission Loss')
    ax.plot(results['timestamp'], abs(results['Q_air_h_W'])/1000, color='#5DADE2', linewidth=0.8, alpha=0.7, label='Ventilation Loss')
    ax.plot(results['timestamp'], results['Q_heat_W']/1000, color='#E74C3C', linewidth=1.2, label='Total Heating Required')
    ax.set_xlabel('Date')
    ax.set_ylabel('Heating Load (kW)')
    ax.set_title('Annual Heating Load Components')
    ax.legend(frameon=False, loc='upper right')
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig


def plot_load_histogram(results):
    """Load distribution histogram with percentiles"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Heating histogram
    heat_data = results.loc[results['Q_heat_W'] > 0, 'Q_heat_W'].values / 1000
    if len(heat_data) > 0:
        # Calculate percentiles
        p004 = np.percentile(heat_data, 0.4)
        p996 = np.percentile(heat_data, 99.6)
        peak = heat_data.max()

        axes[0].hist(heat_data, bins=50, color='#3498DB', alpha=0.7, edgecolor='black', linewidth=0.5)
        axes[0].axvline(p004, color='#27AE60', linestyle='--', linewidth=2, label=f'0.4%: {p004:.1f} kW')
        axes[0].axvline(p996, color='#E74C3C', linestyle='--', linewidth=2, label=f'99.6%: {p996:.1f} kW')
        axes[0].axvline(peak, color='#34495E', linestyle='-', linewidth=2, label=f'Peak: {peak:.1f} kW')
        axes[0].set_xlabel('Heating Load (kW)')
        axes[0].set_ylabel('Frequency (hours)')
        axes[0].set_title('Heating Load Distribution')
        axes[0].legend(frameon=False)
        axes[0].grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.5)
        axes[0].spines['top'].set_visible(False)
        axes[0].spines['right'].set_visible(False)

    # Cooling histogram
    cool_data = results.loc[results['Q_cool_W'] > 0, 'Q_cool_W'].values / 1000
    if len(cool_data) > 0:
        # Calculate percentiles
        p004_c = np.percentile(cool_data, 0.4)
        p996_c = np.percentile(cool_data, 99.6)
        peak_c = cool_data.max()

        axes[1].hist(cool_data, bins=50, color='#E74C3C', alpha=0.7, edgecolor='black', linewidth=0.5)
        axes[1].axvline(p004_c, color='#27AE60', linestyle='--', linewidth=2, label=f'0.4%: {p004_c:.1f} kW')
        axes[1].axvline(p996_c, color='#E74C3C', linestyle='--', linewidth=2, label=f'99.6%: {p996_c:.1f} kW')
        axes[1].axvline(peak_c, color='#34495E', linestyle='-', linewidth=2, label=f'Peak: {peak_c:.1f} kW')
        axes[1].set_xlabel('Cooling Load (kW)')
        axes[1].set_ylabel('Frequency (hours)')
        axes[1].set_title('Cooling Load Distribution')
        axes[1].legend(frameon=False)
        axes[1].grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.5)
        axes[1].spines['top'].set_visible(False)
        axes[1].spines['right'].set_visible(False)

    plt.tight_layout()
    return fig


def main():
    weather = load_epw_weather('weather_files/SWE_ST_Stockholm.Arlanda.AP.024600_TMYx.2004-2018/SWE_ST_Stockholm.Arlanda.AP.024600_TMYx.2004-2018.epw')

    weather['timestamp'] = pd.to_datetime({
        'year': 2018,
        'month': weather['timestamp'].dt.month,
        'day': weather['timestamp'].dt.day,
        'hour': weather['timestamp'].dt.hour
    })
    weather = weather.sort_values('timestamp').reset_index(drop=True)

    print("Annual Energy Simulation")
    print("=" * 50)
    print(f"Total hours: {len(weather)}")
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

    air = AirSide(V_zone_m3=BUILDING_VOLUME, Vdot_vent_m3s=VENT_FLOW, eta_HRV=HRV_EFF, ACH_infiltration_h=INFILTRATION_ACH)

    # Internal gains for cooling (realistic occupancy)
    gains_cooling = InternalGains(Q_equip_kW=EQUIP_GAIN, Q_occ_kW=OCC_GAIN, Q_light_kW=LIGHT_GAIN)

    print("Running annual simulation...")
    print("Design approach:")
    print("  - Heating: Conservative (no internal gains)")
    print("  - Cooling: Realistic (with internal gains)")
    results = run_hourly(weather, planes, air, T_HEAT, T_COOL, gains_cooling)
    print("Simulation complete!")
    print("")

    # Calculate annual totals
    total_heat = results['Q_heat_W'].sum() / 1000
    total_cool = results['Q_cool_W'].sum() / 1000
    total_energy = total_heat + total_cool

    # Calculate energy intensities
    heat_int = total_heat / ATEMP
    cool_int = total_cool / ATEMP
    total_int = total_energy / ATEMP

    # Peak loads with dates
    peak_heat_idx = results['Q_heat_W'].idxmax()
    peak_heat = results.loc[peak_heat_idx, 'Q_heat_W'] / 1000
    peak_heat_date = results.loc[peak_heat_idx, 'timestamp']

    peak_cool_idx = results['Q_cool_W'].idxmax()
    peak_cool = results.loc[peak_cool_idx, 'Q_cool_W'] / 1000
    peak_cool_date = results.loc[peak_cool_idx, 'timestamp']

    # Percentile loads (0.4% and 99.6%)
    heat_data = results.loc[results['Q_heat_W'] > 0, 'Q_heat_W'].values / 1000
    cool_data = results.loc[results['Q_cool_W'] > 0, 'Q_cool_W'].values / 1000

    p004_heat = np.percentile(heat_data, 0.4) if len(heat_data) > 0 else 0
    p996_heat = np.percentile(heat_data, 99.6) if len(heat_data) > 0 else 0

    p004_cool = np.percentile(cool_data, 0.4) if len(cool_data) > 0 else 0
    p996_cool = np.percentile(cool_data, 99.6) if len(cool_data) > 0 else 0

    # Operating hours
    heating_hours = (results['Q_heat_W'] > 0).sum()
    cooling_hours = (results['Q_cool_W'] > 0).sum()
    both_hours = ((results['Q_heat_W'] > 0) & (results['Q_cool_W'] > 0)).sum()
    free_hours = ((results['Q_heat_W'] == 0) & (results['Q_cool_W'] == 0)).sum()

    # Average loads during operation
    avg_heat = results.loc[results['Q_heat_W'] > 0, 'Q_heat_W'].mean() / 1000 if heating_hours > 0 else 0
    avg_cool = results.loc[results['Q_cool_W'] > 0, 'Q_cool_W'].mean() / 1000 if cooling_hours > 0 else 0

    # Load factors
    load_factor_heat = (avg_heat / peak_heat * 100) if peak_heat > 0 else 0
    load_factor_cool = (avg_cool / peak_cool * 100) if peak_cool > 0 else 0

    print("="*80)
    print("ANNUAL ENERGY SUMMARY")
    print("="*80)
    print("")
    print("Annual Energy Consumption:")
    print(f"  Heating:       {total_heat:>10,.0f} kWh/year")
    print(f"  Cooling:       {total_cool:>10,.0f} kWh/year")
    print(f"  Total:         {total_energy:>10,.0f} kWh/year")
    print("")
    print("Energy Intensity (per conditioned area):")
    print(f"  Heating:       {heat_int:>10.1f} kWh/m²·year  ({ATEMP:.0f} m²)")
    print(f"  Cooling:       {cool_int:>10.1f} kWh/m²·year")
    print(f"  Total:         {total_int:>10.1f} kWh/m²·year")
    print("")
    print("Peak Loads:")
    print(f"  Heating:       {peak_heat:>10.1f} kW  ({peak_heat/ATEMP*1000:.1f} W/m²)")
    print(f"                 Date: {peak_heat_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Cooling:       {peak_cool:>10.1f} kW  ({peak_cool/ATEMP*1000:.1f} W/m²)")
    print(f"                 Date: {peak_cool_date.strftime('%Y-%m-%d %H:%M')}")
    print("")
    print("Design Loads (0.4% / 99.6% Percentiles):")
    print(f"  Heating:")
    print(f"    0.4%:        {p004_heat:>10.1f} kW  (min during operation)")
    print(f"    99.6%:       {p996_heat:>10.1f} kW  (design load, excludes 0.4% extremes)")
    print(f"    Peak (100%): {peak_heat:>10.1f} kW  (absolute maximum)")
    print(f"    Sizing:      {p996_heat/peak_heat*100:>10.1f}%  (99.6% as % of peak)")
    print(f"  Cooling:")
    print(f"    0.4%:        {p004_cool:>10.1f} kW  (min during operation)")
    print(f"    99.6%:       {p996_cool:>10.1f} kW  (design load, excludes 0.4% extremes)")
    print(f"    Peak (100%): {peak_cool:>10.1f} kW  (absolute maximum)")
    print(f"    Sizing:      {p996_cool/peak_cool*100:>10.1f}%  (99.6% as % of peak)")
    print("")
    print("Operating Hours:")
    print(f"  Heating:       {heating_hours:>10,} hours  ({heating_hours/8760*100:.1f}% of year)")
    print(f"  Cooling:       {cooling_hours:>10,} hours  ({cooling_hours/8760*100:.1f}% of year)")
    print(f"  Both:          {both_hours:>10,} hours  ({both_hours/8760*100:.1f}% of year)")
    print(f"  Free-running:  {free_hours:>10,} hours  ({free_hours/8760*100:.1f}% of year)")
    print("")
    print("Average Load During Operation:")
    print(f"  Heating:       {avg_heat:>10.1f} kW")
    print(f"  Cooling:       {avg_cool:>10.1f} kW")
    print("")
    print("Load Factors:")
    print(f"  Heating:       {load_factor_heat:>10.1f}%  (avg/peak)")
    print(f"  Cooling:       {load_factor_cool:>10.1f}%  (avg/peak)")
    print("")

    os.makedirs('plots', exist_ok=True)
    print("Generating annual energy plots...")

    fig1 = plot_energy(results)
    fig1.savefig('plots/annual_heating_energy.png', dpi=150, bbox_inches='tight')

    fig2 = plot_breakdown(results)
    fig2.savefig('plots/heating_load_breakdown.png', dpi=150, bbox_inches='tight')

    fig3 = plot_load_histogram(results)
    fig3.savefig('plots/load_distribution_histogram.png', dpi=150, bbox_inches='tight')

    # Generate pie charts for annual heating and cooling breakdown
    fig4 = plot_heat_distribution_4pies(results)
    fig4.savefig('plots/annual_heat_distribution.png', dpi=150, bbox_inches='tight')

    fig5 = plot_heat_distribution_detailed(results, air, gains_cooling, T_HEAT, T_COOL)
    fig5.savefig('plots/annual_heat_distribution_detailed.png', dpi=150, bbox_inches='tight')

    plt.close('all')
    print("Saved plots to plots/ folder:")
    print("  - annual_heating_energy.png (heating focus)")
    print("  - heating_load_breakdown.png (heating components)")
    print("  - load_distribution_histogram.png (load distributions with percentiles)")
    print("  - annual_heat_distribution.png (2-pie: heating/cooling breakdown)")
    print("  - annual_heat_distribution_detailed.png (2-pie: detailed components)")

    return results


if __name__ == '__main__':
    results = main()
