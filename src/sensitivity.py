"""Sensitivity analysis for heating demand."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from config import (FLOOR_AREA, BUILDING_VOLUME, VENT_FLOW, HRV_EFF,
                    INFILTRATION_ACH, INTERNAL_GAIN_W, ALPHA, EPSILON, SHGC,
                    WALL_R, ROOF_R, WINDOW_R, WALL_LAYERS, ROOF_LAYERS,
                    AREA_ROOF, AREA_WALL_N, AREA_WALL_S, AREA_WALL_E, AREA_WALL_W, AREA_WINDOW)
from src.building import Plane, AirSide, InternalGains
from src.physics import run_hourly


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
    'figure.dpi': 150,
    'savefig.dpi': 300,
})

COL_WINTER = '#1a365d'
COL_SHOULDER = '#e67300'


def base_planes(azimuth: float = 180, alpha: float = ALPHA) -> list:
    """Create building planes with given window azimuth and surface absorptance."""
    azimuth_N = (azimuth + 180) % 360
    azimuth_S = azimuth
    azimuth_E = (azimuth + 90) % 360
    azimuth_W = (azimuth + 270) % 360

    roof = Plane('Roof', 'opaque', AREA_ROOF, 0, 0, ROOF_R, alpha, EPSILON)
    wall_N = Plane('Wall-N', 'opaque', AREA_WALL_N, 90, azimuth_N, WALL_R, alpha, EPSILON)
    wall_S = Plane('Wall-S', 'opaque', AREA_WALL_S, 90, azimuth_S, WALL_R, alpha, EPSILON)
    wall_E = Plane('Wall-E', 'opaque', AREA_WALL_E, 90, azimuth_E, WALL_R, alpha, EPSILON)
    wall_W = Plane('Wall-W', 'opaque', AREA_WALL_W, 90, azimuth_W, WALL_R, alpha, EPSILON)
    window_S = Plane('Win-S', 'window', AREA_WINDOW, 90, azimuth_S, WINDOW_R, g=SHGC)

    return [roof, wall_N, wall_S, wall_E, wall_W, window_S]


def planes_with_insulation(k_insulation: float) -> list:
    """Create building planes with varied fiberglass conductivity."""
    # Wall R-value with new insulation
    d_wall_fiberglass = WALL_LAYERS['fiberglass']['d']
    r_wall_other = WALL_R - WALL_LAYERS['fiberglass']['r']
    new_wall_R = r_wall_other + d_wall_fiberglass / k_insulation

    # Roof R-value with new insulation
    d_roof_fiberglass = ROOF_LAYERS['fiberglass']['d']
    r_roof_other = ROOF_R - ROOF_LAYERS['fiberglass']['r']
    new_roof_R = r_roof_other + d_roof_fiberglass / k_insulation

    roof = Plane('Roof', 'opaque', AREA_ROOF, 0, 0, new_roof_R, ALPHA, EPSILON)
    wall_N = Plane('Wall-N', 'opaque', AREA_WALL_N, 90, 0, new_wall_R, ALPHA, EPSILON)
    wall_S = Plane('Wall-S', 'opaque', AREA_WALL_S, 90, 180, new_wall_R, ALPHA, EPSILON)
    wall_E = Plane('Wall-E', 'opaque', AREA_WALL_E, 90, 90, new_wall_R, ALPHA, EPSILON)
    wall_W = Plane('Wall-W', 'opaque', AREA_WALL_W, 90, 270, new_wall_R, ALPHA, EPSILON)
    window_S = Plane('Win-S', 'window', AREA_WINDOW, 90, 180, WINDOW_R, g=SHGC)

    return [roof, wall_N, wall_S, wall_E, wall_W, window_S]


def run_sensitivity(weather: pd.DataFrame, winter_mask, shoulder_mask) -> pd.DataFrame:
    """Run sensitivity analysis for all parameters."""
    results = []
    n_hours = len(weather)

    planes = base_planes()
    air = AirSide(BUILDING_VOLUME, VENT_FLOW, HRV_EFF, INFILTRATION_ACH)
    gains = InternalGains(INTERNAL_GAIN_W / 1000)
    T_set: np.ndarray = np.full(n_hours, 21.0)
    vent_ACH: np.ndarray = np.full(n_hours, 0.5)

    # Baseline
    base_result: pd.DataFrame = run_hourly(weather, planes, air, T_set, vent_ACH=vent_ACH, gains=gains)
    base_winter_kWh = base_result[winter_mask]['Q_heat_W'].sum() / 1000
    base_shoulder_kWh = base_result[shoulder_mask]['Q_heat_W'].sum() / 1000

    # Orientation sensitivity
    orientation_values: np.ndarray = np.arange(0, 360, 30)
    for azimuth in orientation_values:
        result: pd.DataFrame = run_hourly(weather, base_planes(azimuth), air, T_set, vent_ACH=vent_ACH, gains=gains)
        results.append({
            'param': 'Orientation',
            'val': azimuth,
            'val_norm': np.cos(np.deg2rad(azimuth - 180)),
            'Q_w': result[winter_mask]['Q_heat_W'].sum() / 1000,
            'Q_s': result[shoulder_mask]['Q_heat_W'].sum() / 1000,
        })

    # Internal gains sensitivity
    internal_gain_values: np.ndarray = np.linspace(100, 400, 10)
    for Q_internal in internal_gain_values:
        gains_varied = InternalGains(Q_internal / 1000)
        result: pd.DataFrame = run_hourly(weather, planes, air, T_set, vent_ACH=vent_ACH, gains=gains_varied)
        results.append({
            'param': 'Internal gains',
            'val': Q_internal,
            'val_norm': Q_internal / INTERNAL_GAIN_W,
            'Q_w': result[winter_mask]['Q_heat_W'].sum() / 1000,
            'Q_s': result[shoulder_mask]['Q_heat_W'].sum() / 1000,
        })

    # Insulation conductivity sensitivity
    k_values: np.ndarray = np.linspace(0.030, 0.050, 11)
    for k_insulation in k_values:
        result: pd.DataFrame = run_hourly(weather, planes_with_insulation(k_insulation), air, T_set, vent_ACH=vent_ACH, gains=gains)
        results.append({
            'param': 'Insulation k',
            'val': k_insulation,
            'val_norm': k_insulation / 0.040,
            'Q_w': result[winter_mask]['Q_heat_W'].sum() / 1000,
            'Q_s': result[shoulder_mask]['Q_heat_W'].sum() / 1000,
        })

    # Temperature offset sensitivity
    temp_offset_values: np.ndarray = np.linspace(-2, 2, 9)
    for dT in temp_offset_values:
        weather_modified: pd.DataFrame = weather.copy()
        weather_modified['T_out_C'] = weather_modified['T_out_C'] + dT
        result: pd.DataFrame = run_hourly(weather_modified, planes, air, T_set, vent_ACH=vent_ACH, gains=gains)
        results.append({
            'param': 'Temp offset',
            'val': dT,
            'val_norm': dT,
            'Q_w': result[winter_mask]['Q_heat_W'].sum() / 1000,
            'Q_s': result[shoulder_mask]['Q_heat_W'].sum() / 1000,
        })

    # Absorptance sensitivity
    absorptance_values: np.ndarray = np.linspace(0.3, 0.9, 13)
    for alpha_varied in absorptance_values:
        result: pd.DataFrame = run_hourly(weather, base_planes(alpha=alpha_varied), air, T_set, vent_ACH=vent_ACH, gains=gains)
        results.append({
            'param': 'Absorptance',
            'val': alpha_varied,
            'val_norm': alpha_varied / ALPHA,
            'Q_w': result[winter_mask]['Q_heat_W'].sum() / 1000,
            'Q_s': result[shoulder_mask]['Q_heat_W'].sum() / 1000,
        })

    # Infiltration sensitivity
    infiltration_values: np.ndarray = np.linspace(0.2, 1.0, 11)
    for ach_varied in infiltration_values:
        air_varied = AirSide(BUILDING_VOLUME, VENT_FLOW, HRV_EFF, ach_varied)
        result: pd.DataFrame = run_hourly(weather, planes, air_varied, T_set, vent_ACH=vent_ACH, gains=gains)
        results.append({
            'param': 'Infiltration',
            'val': ach_varied,
            'val_norm': ach_varied / INFILTRATION_ACH,
            'Q_w': result[winter_mask]['Q_heat_W'].sum() / 1000,
            'Q_s': result[shoulder_mask]['Q_heat_W'].sum() / 1000,
        })

    df: pd.DataFrame = pd.DataFrame(results)
    df['base_w'] = base_winter_kWh
    df['base_s'] = base_shoulder_kWh
    return df


def calc_nsi(df: pd.DataFrame, param: str, period: str = 'w') -> float:
    """Calculate Normalised Sensitivity Index for a parameter."""
    subset: pd.DataFrame = df[df['param'] == param]
    Q_values: np.ndarray = subset[f'Q_{period}'].values
    base_value = subset[f'base_{period}'].iloc[0]

    if param == 'Orientation':
        return (Q_values.max() - Q_values.min()) / base_value / 2.0
    elif param == 'Temp offset':
        slope, intercept, r_value, p_value, std_err = stats.linregress(subset['val'].values, Q_values)
        return slope / base_value
    else:
        slope, intercept, r_value, p_value, std_err = stats.linregress(subset['val_norm'].values, Q_values / base_value)
        return slope


def calc_sensitivity_table(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate sensitivity table with NSC values and rankings."""
    param_names = ['Orientation', 'Internal gains', 'Insulation k', 'Temp offset', 'Absorptance', 'Infiltration']
    rows = []

    for param in param_names:
        subset: pd.DataFrame = df[df['param'] == param]
        rows.append({
            'Parameter': param,
            'Q_w_min': subset['Q_w'].min(),
            'Q_w_max': subset['Q_w'].max(),
            'NSC_w': calc_nsi(df, param, 'w'),
            'Q_s_min': subset['Q_s'].min(),
            'Q_s_max': subset['Q_s'].max(),
            'NSC_s': calc_nsi(df, param, 's'),
        })

    table: pd.DataFrame = pd.DataFrame(rows)
    table['Rank_w'] = table['NSC_w'].abs().rank(ascending=False).astype(int)
    table['Rank_s'] = table['NSC_s'].abs().rank(ascending=False).astype(int)
    return table


def plot_fig7_scatter(df: pd.DataFrame, path: str) -> None:
    """Plot sensitivity scatter plots with trend lines."""
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()

    param_names = ['Orientation', 'Internal gains', 'Insulation k', 'Temp offset', 'Absorptance', 'Infiltration']
    x_labels = ['Azimuth (deg)', 'Internal Gains (W)', 'Conductivity (W/mK)',
                'Temp Offset (K)', 'Absorptance', 'Infiltration (ACH)']

    for plot_index in range(len(param_names)):
        param = param_names[plot_index]
        x_label = x_labels[plot_index]
        ax = axes[plot_index]

        subset: pd.DataFrame = df[df['param'] == param]
        x_values: np.ndarray = subset['val'].values
        Q_winter: np.ndarray = subset['Q_w'].values
        Q_shoulder: np.ndarray = subset['Q_s'].values

        ax.scatter(x_values, Q_winter, c=COL_WINTER, s=35, edgecolors='white', lw=0.5, label='Winter')
        ax.scatter(x_values, Q_shoulder, c=COL_SHOULDER, s=35, edgecolors='white', lw=0.5, label='Shoulder')

        # Trend lines
        x_fit: np.ndarray = np.linspace(x_values.min(), x_values.max(), 100)

        if param == 'Orientation':
            x_cos: np.ndarray = np.cos(np.deg2rad(x_values - 180))
            x_cos_fit: np.ndarray = np.cos(np.deg2rad(x_fit - 180))

            slope_w, intercept_w, r_w, p_w, se_w = stats.linregress(x_cos, Q_winter)
            slope_s, intercept_s, r_s, p_s, se_s = stats.linregress(x_cos, Q_shoulder)

            ax.plot(x_fit, slope_w * x_cos_fit + intercept_w, '--', c=COL_WINTER, lw=1, alpha=0.7)
            ax.plot(x_fit, slope_s * x_cos_fit + intercept_s, '--', c=COL_SHOULDER, lw=1, alpha=0.7)
            ax.text(0.05, 0.95, f'R²={r_w**2:.3f}', transform=ax.transAxes, fontsize=8, va='top', color=COL_WINTER)
            ax.text(0.05, 0.87, f'R²={r_s**2:.3f}', transform=ax.transAxes, fontsize=8, va='top', color=COL_SHOULDER)
        else:
            slope_w, intercept_w, r_w, p_w, se_w = stats.linregress(x_values, Q_winter)
            slope_s, intercept_s, r_s, p_s, se_s = stats.linregress(x_values, Q_shoulder)

            ax.plot(x_fit, slope_w * x_fit + intercept_w, '--', c=COL_WINTER, lw=1, alpha=0.7)
            ax.plot(x_fit, slope_s * x_fit + intercept_s, '--', c=COL_SHOULDER, lw=1, alpha=0.7)
            ax.text(0.05, 0.95, f'slope={slope_w:.2f}, R²={r_w**2:.3f}', transform=ax.transAxes, fontsize=8, va='top', color=COL_WINTER)
            ax.text(0.05, 0.87, f'slope={slope_s:.2f}, R²={r_s**2:.3f}', transform=ax.transAxes, fontsize=8, va='top', color=COL_SHOULDER)

        ax.set_xlabel(x_label)
        ax.set_ylabel('Weekly Heating (kWh)')
        ax.set_title(param)
        ax.grid(True, alpha=0.3, lw=0.5)

        # Axis margins
        x_margin = (x_values.max() - x_values.min()) * 0.08
        ax.set_xlim(x_values.min() - x_margin, x_values.max() + x_margin)

        all_Q: np.ndarray = np.concatenate([Q_winter, Q_shoulder])
        y_range = all_Q.max() - all_Q.min()
        ax.set_ylim(all_Q.min() - y_range * 0.15, all_Q.max() + y_range * 0.40)

        if plot_index == 0:
            ax.legend(loc='upper right', frameon=True, fontsize=8)

    fig.suptitle('Sensitivity Analysis', fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def plot_fig8_ranking(table: pd.DataFrame, path: str) -> None:
    """Plot horizontal bar chart showing sensitivity ranking."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Color scheme
    COL_WINTER_POS = '#2E5A8B'
    COL_WINTER_NEG = '#5A8AC2'
    COL_SHOULDER_POS = '#D4740C'
    COL_SHOULDER_NEG = '#E9A35A'

    # Sort by average absolute NSC (largest at top)
    table_sorted: pd.DataFrame = table.copy()
    table_sorted['avg_abs'] = (table_sorted['NSC_w'].abs() + table_sorted['NSC_s'].abs()) / 2
    table_sorted = table_sorted.sort_values('avg_abs', ascending=True).reset_index(drop=True)

    y_positions: np.ndarray = np.arange(len(table_sorted))
    bar_height = 0.35

    # Winter bars
    for row_index in range(len(table_sorted)):
        row = table_sorted.iloc[row_index]
        nsc_winter = row['NSC_w']
        color = COL_WINTER_POS if nsc_winter >= 0 else COL_WINTER_NEG
        label = 'Winter' if row_index == 0 else ''
        ax.barh(row_index - bar_height / 2, nsc_winter, bar_height, color=color, edgecolor='none', label=label)

        text_offset = 0.02 if nsc_winter >= 0 else -0.02
        text_align = 'left' if nsc_winter >= 0 else 'right'
        ax.text(nsc_winter + text_offset, row_index - bar_height / 2, f'{nsc_winter:+.3f}',
                va='center', ha=text_align, fontsize=8, color=color)

    # Shoulder bars
    for row_index in range(len(table_sorted)):
        row = table_sorted.iloc[row_index]
        nsc_shoulder = row['NSC_s']
        color = COL_SHOULDER_POS if nsc_shoulder >= 0 else COL_SHOULDER_NEG
        label = 'Shoulder' if row_index == 0 else ''
        ax.barh(row_index + bar_height / 2, nsc_shoulder, bar_height, color=color, edgecolor='none', label=label)

        text_offset = 0.02 if nsc_shoulder >= 0 else -0.02
        text_align = 'left' if nsc_shoulder >= 0 else 'right'
        ax.text(nsc_shoulder + text_offset, row_index + bar_height / 2, f'{nsc_shoulder:+.3f}',
                va='center', ha=text_align, fontsize=8, color=color)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(table_sorted['Parameter'])
    ax.axvline(x=0, color='black', linewidth=0.8)
    ax.set_xlabel('NSC (Normalised Sensitivity Coefficient)')
    ax.grid(True, axis='x', alpha=0.3, lw=0.5)

    max_abs_nsc = max(table_sorted['NSC_w'].abs().max(), table_sorted['NSC_s'].abs().max())
    x_limit = max_abs_nsc * 1.4
    ax.set_xlim(-x_limit, x_limit)

    ax.legend(loc='lower right', frameon=True, fancybox=False)
    ax.set_title('Sensitivity Ranking', fontweight='bold', fontsize=12)

    plt.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
