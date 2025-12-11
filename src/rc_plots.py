"""Plotting functions for RC model comparison."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.dates as mdates

COLORS = {
    'lw': '#2563EB',
    'hw': '#DC2626',
    'outdoor': '#1B4D3E',
    'irr': '#D35400',
    'setpoint': '#888888',
    'dir': '#E74C3C',
    'dif': '#3498DB',
}

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'axes.titleweight': 'bold',
    'axes.linewidth': 0.8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'legend.fontsize': 9,
    'legend.framealpha': 0.95,
    'legend.edgecolor': '#CCCCCC',
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.facecolor': 'white',
})


def _plot_rc_week(res_lw: pd.DataFrame, res_hw: pd.DataFrame, weather: pd.DataFrame,
                  week_start: str, week_end: str, title: str, output_path: str):
    """Plot weekly RC comparison with thermal mass temps and heating load."""

    mask_lw = (res_lw['timestamp'] >= week_start) & (res_lw['timestamp'] < week_end)
    mask_hw = (res_hw['timestamp'] >= week_start) & (res_hw['timestamp'] < week_end)

    data_lw = res_lw[mask_lw].reset_index(drop=True)
    data_hw = res_hw[mask_hw].reset_index(drop=True)

    # Interpolate weather to match results timestep
    weather_hourly = weather.copy().set_index('timestamp')
    weather_interp = weather_hourly.resample('15min').interpolate(method='linear').reset_index()
    mask_weather = (weather_interp['timestamp'] >= week_start) & (weather_interp['timestamp'] < week_end)
    data_weather = weather_interp[mask_weather].reset_index(drop=True)

    n_steps = len(data_lw)
    steps = np.arange(n_steps)

    # X-axis labels: show 00:00 and 12:00
    timestamps = data_lw['timestamp']
    tick_positions = []
    tick_labels = []
    for i, ts in enumerate(timestamps):
        if ts.hour == 0 and ts.minute == 0:
            tick_positions.append(i)
            tick_labels.append(ts.strftime('%a %d/%m\n00:00'))
        elif ts.hour == 12 and ts.minute == 0:
            tick_positions.append(i)
            tick_labels.append('12:00')

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    # Panel 1: Lightweight thermal mass temps
    ax1 = axes[0]
    ax1.plot(steps, data_lw['T_C_roof'], lw=1.2, label='Roof')
    ax1.plot(steps, data_lw['T_C_N'], lw=1.2, label='North')
    ax1.plot(steps, data_lw['T_C_S'], lw=1.2, label='South')
    ax1.plot(steps, data_lw['T_C_E'], lw=1.2, label='East')
    ax1.plot(steps, data_lw['T_C_W'], lw=1.2, label='West')
    ax1.plot(steps, data_weather['T_out_C'], 'k--', lw=1, label='Outdoor')
    ax1.set_ylabel('Temperature (°C)')
    ax1.set_ylim(-5, 30)
    ax1.legend(loc='upper right', ncol=3, frameon=True, fancybox=False, fontsize=8)
    ax1.grid(True, alpha=0.3, lw=0.5)
    ax1.set_title('Lightweight (Case 600) - Thermal Mass Temperatures')

    # Add irradiance on right axis
    ax1_irr = ax1.twinx()
    data_weather['GHI'] = data_weather['I_dir_Wm2'] + data_weather['I_dif_Wm2']
    ax1_irr.fill_between(steps, data_weather['GHI'], alpha=0.2, color=COLORS['irr'])
    ax1_irr.set_ylabel('Irradiance (W/m²)', color=COLORS['irr'])
    ax1_irr.tick_params(axis='y', labelcolor=COLORS['irr'])
    ax1_irr.set_ylim(0, 1000)
    ax1_irr.spines['right'].set_visible(True)
    ax1_irr.spines['right'].set_color(COLORS['irr'])

    # Panel 2: Heavyweight thermal mass temps
    ax2 = axes[1]
    ax2.plot(steps, data_hw['T_C_roof'], lw=1.2, label='Roof')
    ax2.plot(steps, data_hw['T_C_N'], lw=1.2, label='North')
    ax2.plot(steps, data_hw['T_C_S'], lw=1.2, label='South')
    ax2.plot(steps, data_hw['T_C_E'], lw=1.2, label='East')
    ax2.plot(steps, data_hw['T_C_W'], lw=1.2, label='West')
    ax2.plot(steps, data_weather['T_out_C'], 'k--', lw=1, label='Outdoor')
    ax2.set_ylabel('Temperature (°C)')
    ax2.set_ylim(-5, 30)
    ax2.legend(loc='upper right', ncol=3, frameon=True, fancybox=False, fontsize=8)
    ax2.grid(True, alpha=0.3, lw=0.5)
    ax2.set_title('Heavyweight (Case 900) - Thermal Mass Temperatures')

    ax2_irr = ax2.twinx()
    ax2_irr.fill_between(steps, data_weather['GHI'], alpha=0.2, color=COLORS['irr'])
    ax2_irr.set_ylabel('Irradiance (W/m²)', color=COLORS['irr'])
    ax2_irr.tick_params(axis='y', labelcolor=COLORS['irr'])
    ax2_irr.set_ylim(0, 1000)
    ax2_irr.spines['right'].set_visible(True)
    ax2_irr.spines['right'].set_color(COLORS['irr'])

    # Panel 3: Heating load comparison (area chart)
    ax3 = axes[2]
    Q_lw = data_lw['Q_heat_W'].values / 1000
    Q_hw = data_hw['Q_heat_W'].values / 1000

    ax3.fill_between(steps, Q_lw, alpha=0.5, color=COLORS['lw'], label='Lightweight')
    ax3.fill_between(steps, Q_hw, alpha=0.5, color=COLORS['hw'], label='Heavyweight')
    ax3.plot(steps, Q_lw, color=COLORS['lw'], lw=1.2)
    ax3.plot(steps, Q_hw, color=COLORS['hw'], lw=1.2)

    ax3.set_ylabel('Heating Load (kW)')
    ax3.set_xlabel('Date/Time')
    ax3.set_ylim(0, 3.5)
    ax3.legend(loc='upper right', frameon=True, fancybox=False)
    ax3.grid(True, alpha=0.3, lw=0.5)
    ax3.set_title('Heating Load Comparison')

    # Add outdoor temp on right axis
    ax3_temp = ax3.twinx()
    ax3_temp.plot(steps, data_weather['T_out_C'], color=COLORS['outdoor'], lw=1.5, ls='--',
                  label='Outdoor Temp')
    ax3_temp.set_ylabel('Outdoor Temp (°C)', color=COLORS['outdoor'])
    ax3_temp.tick_params(axis='y', labelcolor=COLORS['outdoor'])
    ax3_temp.set_ylim(-10, 25)
    ax3_temp.spines['right'].set_visible(True)
    ax3_temp.spines['right'].set_color(COLORS['outdoor'])

    # X-axis formatting
    ax3.set_xticks(tick_positions)
    ax3.set_xticklabels(tick_labels, rotation=0)
    ax3.set_xlim(0, n_steps - 1)

    fig.suptitle(title, fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_rc_winter_week(res_lw: pd.DataFrame, res_hw: pd.DataFrame, weather: pd.DataFrame,
                        output_path: str = 'outputs/rc_winter_week.png'):
    """Plot winter week comparison."""
    _plot_rc_week(res_lw, res_hw, weather,
                  '2021-01-11', '2021-01-18',
                  'Winter Week (11-17 January)',
                  output_path)


def plot_rc_heatup_week(res_lw: pd.DataFrame, res_hw: pd.DataFrame, weather: pd.DataFrame,
                        output_path: str = 'outputs/rc_heatup_week.png'):
    """Plot first week showing thermal mass warm-up from initial 10°C."""
    week_start, week_end = '2021-01-01', '2021-01-08'

    mask_lw = (res_lw['timestamp'] >= week_start) & (res_lw['timestamp'] < week_end)
    mask_hw = (res_hw['timestamp'] >= week_start) & (res_hw['timestamp'] < week_end)

    data_lw = res_lw[mask_lw].reset_index(drop=True)
    data_hw = res_hw[mask_hw].reset_index(drop=True)

    # Interpolate weather
    weather_hourly = weather.copy().set_index('timestamp')
    weather_interp = weather_hourly.resample('15min').interpolate(method='linear').reset_index()
    mask_weather = (weather_interp['timestamp'] >= week_start) & (weather_interp['timestamp'] < week_end)
    data_weather = weather_interp[mask_weather].reset_index(drop=True)

    n_steps = len(data_lw)
    steps = np.arange(n_steps)

    # X-axis labels - show 00:00 and 12:00
    timestamps = data_lw['timestamp']
    tick_positions = []
    tick_labels = []
    for i, ts in enumerate(timestamps):
        if ts.hour == 0 and ts.minute == 0:
            tick_positions.append(i)
            tick_labels.append(ts.strftime('%a %d/%m\n00:00'))
        elif ts.hour == 12 and ts.minute == 0:
            tick_positions.append(i)
            tick_labels.append('12:00')

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Panel 1: South wall thermal mass temps
    ax1 = axes[0]
    ax1.plot(steps, data_lw['T_C_S'], color=COLORS['lw'], lw=1.5, label='Lightweight')
    ax1.plot(steps, data_hw['T_C_S'], color=COLORS['hw'], lw=1.5, label='Heavyweight')
    ax1.plot(steps, data_weather['T_out_C'], color=COLORS['outdoor'], ls='--', lw=1.2, label='Outdoor')
    ax1.axhline(21, color=COLORS['setpoint'], ls=':', lw=1, label='Setpoint (21°C)')
    ax1.axhline(10, color='gray', ls=':', lw=1, alpha=0.5, label='Initial (10°C)')

    ax1.set_ylabel('Temperature (°C)')
    ax1.set_ylim(0, 25)
    ax1.legend(loc='lower right', frameon=True, fancybox=False, ncol=2)
    ax1.grid(True, alpha=0.3, lw=0.5)
    ax1.set_title('Heat-up Week - South Wall Thermal Mass Temperature (Initial T=10°C)')

    # Irradiance on right axis
    ax1_irr = ax1.twinx()
    data_weather['GHI'] = data_weather['I_dir_Wm2'] + data_weather['I_dif_Wm2']
    ax1_irr.fill_between(steps, data_weather['GHI'], alpha=0.15, color=COLORS['irr'])
    ax1_irr.set_ylabel('Solar Irradiance (W/m²)', color=COLORS['irr'])
    ax1_irr.tick_params(axis='y', labelcolor=COLORS['irr'])
    ax1_irr.set_ylim(0, 800)
    ax1_irr.spines['right'].set_visible(True)
    ax1_irr.spines['right'].set_color(COLORS['irr'])

    # Panel 2: Heating load
    ax2 = axes[1]
    Q_lw = data_lw['Q_heat_W'].values / 1000
    Q_hw = data_hw['Q_heat_W'].values / 1000

    ax2.fill_between(steps, Q_lw, alpha=0.4, color=COLORS['lw'], label='Lightweight')
    ax2.fill_between(steps, Q_hw, alpha=0.4, color=COLORS['hw'], label='Heavyweight')
    ax2.plot(steps, Q_lw, color=COLORS['lw'], lw=1.2)
    ax2.plot(steps, Q_hw, color=COLORS['hw'], lw=1.2)

    ax2.set_ylabel('Heating Load (kW)')
    ax2.set_xlabel('Date')
    ax2.set_ylim(0, max(Q_lw.max(), Q_hw.max()) * 1.1)
    ax2.legend(loc='upper right', frameon=True, fancybox=False)
    ax2.grid(True, alpha=0.3, lw=0.5)
    ax2.set_title('Heat-up Week - Heating Load Comparison')

    # Outdoor temp on right axis
    ax2_temp = ax2.twinx()
    ax2_temp.plot(steps, data_weather['T_out_C'], color=COLORS['outdoor'], lw=1.5, ls='--')
    ax2_temp.set_ylabel('Outdoor Temp (°C)', color=COLORS['outdoor'])
    ax2_temp.tick_params(axis='y', labelcolor=COLORS['outdoor'])
    ax2_temp.set_ylim(-5, 15)
    ax2_temp.spines['right'].set_visible(True)
    ax2_temp.spines['right'].set_color(COLORS['outdoor'])

    # Weekly totals
    total_lw = Q_lw.sum() * 0.25
    total_hw = Q_hw.sum() * 0.25
    pct_diff = (total_hw - total_lw) / total_lw * 100
    stats_text = f'Weekly total: LW={total_lw:.1f} kWh, HW={total_hw:.1f} kWh ({pct_diff:+.1f}%)'
    ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes, fontsize=9, va='top', ha='left',
             bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.9))

    ax2.set_xticks(tick_positions)
    ax2.set_xticklabels(tick_labels)
    ax2.set_xlim(0, n_steps - 1)

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_rc_shoulder_week(res_lw: pd.DataFrame, res_hw: pd.DataFrame, weather: pd.DataFrame,
                          output_path: str = 'outputs/rc_shoulder_week.png'):
    """Plot shoulder week - South wall temp comparison (LW vs HW merged)."""
    week_start, week_end = '2021-10-07', '2021-10-14'

    mask_lw = (res_lw['timestamp'] >= week_start) & (res_lw['timestamp'] < week_end)
    mask_hw = (res_hw['timestamp'] >= week_start) & (res_hw['timestamp'] < week_end)

    data_lw = res_lw[mask_lw].reset_index(drop=True)
    data_hw = res_hw[mask_hw].reset_index(drop=True)

    # Interpolate weather
    weather_hourly = weather.copy().set_index('timestamp')
    weather_interp = weather_hourly.resample('15min').interpolate(method='linear').reset_index()
    mask_weather = (weather_interp['timestamp'] >= week_start) & (weather_interp['timestamp'] < week_end)
    data_weather = weather_interp[mask_weather].reset_index(drop=True)

    n_steps = len(data_lw)
    steps = np.arange(n_steps)

    # X-axis labels - show 00:00 and 12:00
    timestamps = data_lw['timestamp']
    tick_positions = []
    tick_labels = []
    for i, ts in enumerate(timestamps):
        if ts.hour == 0 and ts.minute == 0:
            tick_positions.append(i)
            tick_labels.append(ts.strftime('%a %d/%m\n00:00'))
        elif ts.hour == 12 and ts.minute == 0:
            tick_positions.append(i)
            tick_labels.append('12:00')

    fig, ax = plt.subplots(figsize=(12, 5))

    # South wall thermal mass temps - both cases on same chart
    ax.plot(steps, data_lw['T_C_S'], color=COLORS['lw'], lw=1.5, label='Lightweight')
    ax.plot(steps, data_hw['T_C_S'], color=COLORS['hw'], lw=1.5, label='Heavyweight')
    ax.plot(steps, data_weather['T_out_C'], color=COLORS['outdoor'], ls='--', lw=1.2, label='Outdoor')
    ax.axhline(21, color=COLORS['setpoint'], ls=':', lw=1, label='Setpoint (21°C)')

    ax.set_ylabel('Temperature (°C)')
    ax.set_xlabel('Date')
    ax.set_ylim(0, 25)
    ax.legend(loc='lower right', frameon=True, fancybox=False)
    ax.grid(True, alpha=0.3, lw=0.5)
    ax.set_title('Shoulder Week - South Wall Thermal Mass Temperature')

    # Irradiance on right axis
    ax_irr = ax.twinx()
    data_weather['GHI'] = data_weather['I_dir_Wm2'] + data_weather['I_dif_Wm2']
    ax_irr.fill_between(steps, data_weather['GHI'], alpha=0.15, color=COLORS['irr'])
    ax_irr.set_ylabel('Solar Irradiance (W/m²)', color=COLORS['irr'])
    ax_irr.tick_params(axis='y', labelcolor=COLORS['irr'])
    ax_irr.set_ylim(0, 800)
    ax_irr.spines['right'].set_visible(True)
    ax_irr.spines['right'].set_color(COLORS['irr'])

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels)
    ax.set_xlim(0, n_steps - 1)

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_rc_shoulder_heating(res_lw: pd.DataFrame, res_hw: pd.DataFrame, weather: pd.DataFrame,
                              output_path: str = 'outputs/rc_shoulder_heating.png'):
    """Plot shoulder week - Heating load comparison."""
    week_start, week_end = '2021-10-07', '2021-10-14'

    mask_lw = (res_lw['timestamp'] >= week_start) & (res_lw['timestamp'] < week_end)
    mask_hw = (res_hw['timestamp'] >= week_start) & (res_hw['timestamp'] < week_end)

    data_lw = res_lw[mask_lw].reset_index(drop=True)
    data_hw = res_hw[mask_hw].reset_index(drop=True)

    # Interpolate weather
    weather_hourly = weather.copy().set_index('timestamp')
    weather_interp = weather_hourly.resample('15min').interpolate(method='linear').reset_index()
    mask_weather = (weather_interp['timestamp'] >= week_start) & (weather_interp['timestamp'] < week_end)
    data_weather = weather_interp[mask_weather].reset_index(drop=True)

    n_steps = len(data_lw)
    steps = np.arange(n_steps)

    # X-axis labels - show 00:00 and 12:00
    timestamps = data_lw['timestamp']
    tick_positions = []
    tick_labels = []
    for i, ts in enumerate(timestamps):
        if ts.hour == 0 and ts.minute == 0:
            tick_positions.append(i)
            tick_labels.append(ts.strftime('%a %d/%m\n00:00'))
        elif ts.hour == 12 and ts.minute == 0:
            tick_positions.append(i)
            tick_labels.append('12:00')

    fig, ax = plt.subplots(figsize=(12, 5))

    Q_lw = data_lw['Q_heat_W'].values / 1000
    Q_hw = data_hw['Q_heat_W'].values / 1000

    ax.fill_between(steps, Q_lw, alpha=0.4, color=COLORS['lw'], label='Lightweight')
    ax.fill_between(steps, Q_hw, alpha=0.4, color=COLORS['hw'], label='Heavyweight')
    ax.plot(steps, Q_lw, color=COLORS['lw'], lw=1.2)
    ax.plot(steps, Q_hw, color=COLORS['hw'], lw=1.2)

    ax.set_ylabel('Heating Load (kW)')
    ax.set_xlabel('Date')
    ax.set_ylim(0, 2.5)
    ax.legend(loc='upper right', frameon=True, fancybox=False)
    ax.grid(True, alpha=0.3, lw=0.5)
    ax.set_title('Shoulder Week - Heating Load Comparison')

    # Outdoor temp on right axis
    ax_temp = ax.twinx()
    ax_temp.plot(steps, data_weather['T_out_C'], color=COLORS['outdoor'], lw=1.5, ls='--')
    ax_temp.set_ylabel('Outdoor Temp (°C)', color=COLORS['outdoor'])
    ax_temp.tick_params(axis='y', labelcolor=COLORS['outdoor'])
    ax_temp.set_ylim(0, 25)
    ax_temp.spines['right'].set_visible(True)
    ax_temp.spines['right'].set_color(COLORS['outdoor'])

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels)
    ax.set_xlim(0, n_steps - 1)

    # Add weekly totals
    total_lw = Q_lw.sum() * 0.25  # kWh (15-min intervals)
    total_hw = Q_hw.sum() * 0.25
    pct_diff = (total_hw - total_lw) / total_lw * 100
    stats_text = f'Weekly total: LW={total_lw:.1f} kWh, HW={total_hw:.1f} kWh ({pct_diff:+.1f}%)'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9, va='top', ha='left',
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.9))

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_heating_histogram(res_lw, res_hw, output_path='outputs/rc_heating_histogram.png'):
    """Plot heating load distribution histogram."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    Q_lw: np.ndarray = res_lw['Q_heat_W'].values / 1000
    Q_hw: np.ndarray = res_hw['Q_heat_W'].values / 1000

    Q_lw_nonzero = Q_lw[Q_lw > 0]
    Q_hw_nonzero = Q_hw[Q_hw > 0]

    mean_lw = Q_lw_nonzero.mean()
    std_lw = Q_lw_nonzero.std()
    mean_hw = Q_hw_nonzero.mean()
    std_hw = Q_hw_nonzero.std()

    bins = np.linspace(0, 3.5, 36)

    ax1 = axes[0]
    ax1.hist(Q_lw_nonzero, bins=bins, color=COLORS['lw'], alpha=0.7, edgecolor='white')
    ax1.axvline(mean_lw, color='k', ls='--', lw=1.5, label=f'Mean: {mean_lw:.2f} kW')
    ax1.axvline(mean_lw - std_lw, color='k', ls=':', lw=1)
    ax1.axvline(mean_lw + std_lw, color='k', ls=':', lw=1, label=f'Std: {std_lw:.2f} kW')
    ax1.set_xlabel('Heating Load (kW)')
    ax1.set_ylabel('Hours')
    ax1.set_title('Lightweight (Case 600)')
    ax1.legend(loc='upper right', frameon=True, fancybox=False)
    ax1.grid(True, alpha=0.3, lw=0.5)
    ax1.set_xlim(0, 3.5)

    ax2 = axes[1]
    ax2.hist(Q_hw_nonzero, bins=bins, color=COLORS['hw'], alpha=0.7, edgecolor='white')
    ax2.axvline(mean_hw, color='k', ls='--', lw=1.5, label=f'Mean: {mean_hw:.2f} kW')
    ax2.axvline(mean_hw - std_hw, color='k', ls=':', lw=1)
    ax2.axvline(mean_hw + std_hw, color='k', ls=':', lw=1, label=f'Std: {std_hw:.2f} kW')
    ax2.set_xlabel('Heating Load (kW)')
    ax2.set_ylabel('Hours')
    ax2.set_title('Heavyweight (Case 900)')
    ax2.legend(loc='upper right', frameon=True, fancybox=False)
    ax2.grid(True, alpha=0.3, lw=0.5)
    ax2.set_xlim(0, 3.5)

    fig.suptitle('Heating Load Distribution (non-zero hours)', fontsize=12, fontweight='bold')
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_heating_comparison_histogram(res_lw, res_hw, output_path='outputs/rc_heating_comparison.png'):
    """Plot overlaid heating load histograms with mean/std annotations."""
    fig, ax = plt.subplots(figsize=(10, 6))

    Q_lw: np.ndarray = res_lw['Q_heat_W'].values / 1000
    Q_hw: np.ndarray = res_hw['Q_heat_W'].values / 1000

    Q_lw_nonzero = Q_lw[Q_lw > 0]
    Q_hw_nonzero = Q_hw[Q_hw > 0]

    mean_lw, std_lw = Q_lw_nonzero.mean(), Q_lw_nonzero.std()
    mean_hw, std_hw = Q_hw_nonzero.mean(), Q_hw_nonzero.std()

    bins = np.linspace(0, 3.5, 36)

    # Histograms
    ax.hist(Q_lw_nonzero, bins=bins, color=COLORS['lw'], alpha=0.5, edgecolor=COLORS['lw'],
            label='Lightweight')
    ax.hist(Q_hw_nonzero, bins=bins, color=COLORS['hw'], alpha=0.5, edgecolor=COLORS['hw'],
            label='Heavyweight')

    # Mean lines
    ax.axvline(mean_lw, color=COLORS['lw'], ls='--', lw=2, label=f'LW mean: {mean_lw:.2f} kW')
    ax.axvline(mean_hw, color=COLORS['hw'], ls='--', lw=2, label=f'HW mean: {mean_hw:.2f} kW')

    # Std deviation bands
    ax.axvspan(mean_lw - std_lw, mean_lw + std_lw, alpha=0.15, color=COLORS['lw'])
    ax.axvspan(mean_hw - std_hw, mean_hw + std_hw, alpha=0.15, color=COLORS['hw'])

    ax.set_xlabel('Heating Load (kW)')
    ax.set_ylabel('Hours')
    ax.set_title('Heating Load Distribution Comparison (non-zero hours)')
    ax.legend(loc='upper right', frameon=True, fancybox=False)
    ax.grid(True, alpha=0.3, lw=0.5)
    ax.set_xlim(0, 3.5)

    # Stats text box
    stats_text = (f'Lightweight:  mean={mean_lw:.2f} kW, std={std_lw:.2f} kW\n'
                  f'Heavyweight: mean={mean_hw:.2f} kW, std={std_hw:.2f} kW')
    ax.text(0.98, 0.75, stats_text, transform=ax.transAxes, fontsize=9, va='top', ha='right',
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.9),
            family='monospace')

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_monthly_peak_demand(res_lw, res_hw, output_path='outputs/rc_peak_demand.png'):
    """Plot monthly peak heating demand comparison."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Skip first day to avoid warm-up transient affecting peak
    res_lw = res_lw[res_lw['timestamp'] >= '2021-01-02'].copy()
    res_hw = res_hw[res_hw['timestamp'] >= '2021-01-02'].copy()

    # Get monthly max heating load
    res_lw['month'] = res_lw['timestamp'].dt.month
    res_hw['month'] = res_hw['timestamp'].dt.month

    monthly_lw = res_lw.groupby('month')['Q_heat_W'].max() / 1000
    monthly_hw = res_hw.groupby('month')['Q_heat_W'].max() / 1000

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    x = np.arange(12)
    width = 0.35

    bars_lw = ax.bar(x - width/2, monthly_lw.values, width, color=COLORS['lw'], label='Lightweight')
    bars_hw = ax.bar(x + width/2, monthly_hw.values, width, color=COLORS['hw'], label='Heavyweight')

    # Add value labels inside bars
    for bar, val in zip(bars_lw, monthly_lw.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 0.15,
                f'{val:.2f}', ha='center', va='top', fontsize=7, color='white', fontweight='bold')
    for bar, val in zip(bars_hw, monthly_hw.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 0.15,
                f'{val:.2f}', ha='center', va='top', fontsize=7, color='white', fontweight='bold')

    # Add % difference labels above bars
    for i, (lw_val, hw_val) in enumerate(zip(monthly_lw.values, monthly_hw.values)):
        pct_diff = (hw_val - lw_val) / lw_val * 100
        y_pos = max(lw_val, hw_val) + 0.1
        ax.text(x[i], y_pos, f'{pct_diff:.1f}%', ha='center', va='bottom', fontsize=7,
                color=COLORS['hw'] if pct_diff < 0 else 'black')

    ax.set_xlabel('Month')
    ax.set_ylabel('Peak Heating Demand (kW)')
    ax.set_title('Monthly Peak Heating Demand')
    ax.set_xticks(x)
    ax.set_xticklabels(months)

    # Set ylim to fit all labels
    max_val = max(monthly_lw.max(), monthly_hw.max())
    ax.set_ylim(0, max_val + 0.8)

    ax.legend(loc='upper right', frameon=True, fancybox=False)
    ax.grid(True, alpha=0.3, lw=0.5, axis='y')

    # Add annual peak info
    annual_lw = monthly_lw.max()
    annual_hw = monthly_hw.max()
    pct_diff = (annual_hw - annual_lw) / annual_lw * 100
    ax.text(0.02, 0.98, f'Annual peak: LW={annual_lw:.2f} kW, HW={annual_hw:.2f} kW ({pct_diff:+.1f}%)',
            transform=ax.transAxes, fontsize=9, va='top', ha='left',
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.9))

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_glasgow_weather(weather: pd.DataFrame, output_path: str = 'outputs/glasgow_weather.png'):
    """Plot Glasgow annual weather data for report introduction.

    Shows dry bulb temperature and solar irradiance (direct + diffuse) to illustrate
    cloudy, heating-dominated climate.
    """
    weather = weather.copy()
    weather['timestamp'] = pd.to_datetime(weather['timestamp'])
    weather = weather.set_index('timestamp')

    # Resample to daily for cleaner visualization
    daily = weather.resample('D').agg({
        'T_out_C': ['mean', 'min', 'max'],
        'I_dir_Wm2': 'mean',
        'I_dif_Wm2': 'mean',
    })
    daily.columns = ['T_mean', 'T_min', 'T_max', 'I_dir', 'I_dif']
    daily['GHI'] = daily['I_dir'] + daily['I_dif']

    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

    # Panel 1: Temperature
    ax1 = axes[0]
    ax1.fill_between(daily.index, daily['T_min'], daily['T_max'],
                     alpha=0.3, color=COLORS['outdoor'], label='Daily range')
    ax1.plot(daily.index, daily['T_mean'], color=COLORS['outdoor'], lw=1.2, label='Daily mean')
    ax1.axhline(21, color=COLORS['setpoint'], ls=':', lw=1, label='Comfort (21°C)')
    ax1.axhline(0, color='gray', ls='--', lw=0.8, alpha=0.5)

    ax1.set_ylabel('Dry Bulb Temperature (°C)')
    ax1.set_ylim(-10, 30)
    ax1.legend(loc='upper right', frameon=True, fancybox=False)
    ax1.grid(True, alpha=0.3, lw=0.5)
    ax1.set_title('Glasgow Annual Temperature')

    # Panel 2: Solar irradiance
    ax2 = axes[1]
    ax2.fill_between(daily.index, 0, daily['I_dif'], alpha=0.6, color=COLORS['dif'],
                     label='Diffuse Horizontal Irradiance')
    ax2.fill_between(daily.index, daily['I_dif'], daily['GHI'], alpha=0.6, color=COLORS['dir'],
                     label='Direct Normal Irradiance')

    ax2.set_ylabel('Daily Mean Irradiance (W/m²)')
    ax2.set_xlabel('Month')
    # Set ylim with gap above max value
    max_irr = daily['GHI'].max()
    ax2.set_ylim(0, max_irr * 1.15)
    ax2.legend(loc='upper right', frameon=True, fancybox=False)
    ax2.grid(True, alpha=0.3, lw=0.5)
    ax2.set_title('Glasgow Annual Solar Irradiance')

    # Format x-axis with months
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

    # Add stats text
    mean_temp = weather['T_out_C'].mean()
    heating_hours = (weather['T_out_C'] < 15).sum()
    heating_pct = heating_hours / len(weather) * 100

    stats_text = (f'Mean temp: {mean_temp:.1f}°C\n'
                  f'Hours below 15°C: {heating_hours} ({heating_pct:.0f}%)')
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, fontsize=9, va='top', ha='left',
             bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.9),
             family='monospace')

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"Saved: {output_path}")
