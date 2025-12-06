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


def base_planes(azimuth=180, alpha=ALPHA):
    return [
        Plane('Roof',   'opaque', AREA_ROOF,   0,  0,                     ROOF_R, alpha, EPSILON),
        Plane('Wall-N', 'opaque', AREA_WALL_N, 90, (azimuth+180) % 360,   WALL_R, alpha, EPSILON),
        Plane('Wall-S', 'opaque', AREA_WALL_S, 90, azimuth,               WALL_R, alpha, EPSILON),
        Plane('Wall-E', 'opaque', AREA_WALL_E, 90, (azimuth+90) % 360,    WALL_R, alpha, EPSILON),
        Plane('Wall-W', 'opaque', AREA_WALL_W, 90, (azimuth+270) % 360,   WALL_R, alpha, EPSILON),
        Plane('Win-S',  'window', AREA_WINDOW, 90, azimuth,               WINDOW_R, g=SHGC),
    ]


def planes_with_insulation(k_ins):
    """Vary fiberglass conductivity, recalc total r."""
    # wall
    d_wall = WALL_LAYERS['fiberglass']['d']
    r_wall_other = WALL_R - WALL_LAYERS['fiberglass']['r']
    new_wall_r = r_wall_other + d_wall / k_ins

    # roof
    d_roof = ROOF_LAYERS['fiberglass']['d']
    r_roof_other = ROOF_R - ROOF_LAYERS['fiberglass']['r']
    new_roof_r = r_roof_other + d_roof / k_ins

    return [
        Plane('Roof',   'opaque', AREA_ROOF,   0,  0,   new_roof_r, ALPHA, EPSILON),
        Plane('Wall-N', 'opaque', AREA_WALL_N, 90, 0,   new_wall_r, ALPHA, EPSILON),
        Plane('Wall-S', 'opaque', AREA_WALL_S, 90, 180, new_wall_r, ALPHA, EPSILON),
        Plane('Wall-E', 'opaque', AREA_WALL_E, 90, 90,  new_wall_r, ALPHA, EPSILON),
        Plane('Wall-W', 'opaque', AREA_WALL_W, 90, 270, new_wall_r, ALPHA, EPSILON),
        Plane('Win-S',  'window', AREA_WINDOW, 90, 180, WINDOW_R, g=SHGC),
    ]


def run_sensitivity(weather, winter_mask, shoulder_mask):
    results = []

    planes = base_planes()
    air = AirSide(BUILDING_VOLUME, VENT_FLOW, HRV_EFF, INFILTRATION_ACH)
    gains = InternalGains(INTERNAL_GAIN_W / 1000)
    T_set = np.full(len(weather), 21.0)
    vent = np.full(len(weather), 0.5)

    base = run_hourly(weather, planes, air, T_set, vent_ACH=vent, gains=gains)
    base_w = base[winter_mask]['Q_heat_W'].sum() / 1000
    base_s = base[shoulder_mask]['Q_heat_W'].sum() / 1000

    # orientation
    print("  Orientation...")
    for az in np.arange(0, 360, 30):
        res = run_hourly(weather, base_planes(az), air, T_set, vent_ACH=vent, gains=gains)
        results.append({
            'param': 'Orientation', 'val': az,
            'val_norm': np.cos(np.deg2rad(az - 180)),
            'Q_w': res[winter_mask]['Q_heat_W'].sum()/1000,
            'Q_s': res[shoulder_mask]['Q_heat_W'].sum()/1000,
        })

    # internal gains
    print("  Internal gains...")
    for Q in np.linspace(100, 400, 10):
        g = InternalGains(Q / 1000)
        res = run_hourly(weather, planes, air, T_set, vent_ACH=vent, gains=g)
        results.append({
            'param': 'Internal gains', 'val': Q,
            'val_norm': Q / INTERNAL_GAIN_W,
            'Q_w': res[winter_mask]['Q_heat_W'].sum()/1000,
            'Q_s': res[shoulder_mask]['Q_heat_W'].sum()/1000,
        })

    # insulation conductivity
    print("  Insulation conductivity...")
    for k in np.linspace(0.030, 0.050, 11):
        res = run_hourly(weather, planes_with_insulation(k), air, T_set, vent_ACH=vent, gains=gains)
        results.append({
            'param': 'Insulation k', 'val': k,
            'val_norm': k / 0.040,
            'Q_w': res[winter_mask]['Q_heat_W'].sum()/1000,
            'Q_s': res[shoulder_mask]['Q_heat_W'].sum()/1000,
        })

    # temperature offset
    print("  Temperature offset...")
    for dT in np.linspace(-2, 2, 9):
        w_mod = weather.copy()
        w_mod['T_out_C'] = w_mod['T_out_C'] + dT
        res = run_hourly(w_mod, planes, air, T_set, vent_ACH=vent, gains=gains)
        results.append({
            'param': 'Temp offset', 'val': dT,
            'val_norm': dT,
            'Q_w': res[winter_mask]['Q_heat_W'].sum()/1000,
            'Q_s': res[shoulder_mask]['Q_heat_W'].sum()/1000,
        })

    # absorptance
    print("  Surface absorptance...")
    for a in np.linspace(0.3, 0.9, 13):
        res = run_hourly(weather, base_planes(alpha=a), air, T_set, vent_ACH=vent, gains=gains)
        results.append({
            'param': 'Absorptance', 'val': a,
            'val_norm': a / ALPHA,
            'Q_w': res[winter_mask]['Q_heat_W'].sum()/1000,
            'Q_s': res[shoulder_mask]['Q_heat_W'].sum()/1000,
        })

    # infiltration
    print("  Infiltration ACH...")
    for ach in np.linspace(0.2, 1.0, 11):
        a_var = AirSide(BUILDING_VOLUME, VENT_FLOW, HRV_EFF, ach)
        res = run_hourly(weather, planes, a_var, T_set, vent_ACH=vent, gains=gains)
        results.append({
            'param': 'Infiltration', 'val': ach,
            'val_norm': ach / INFILTRATION_ACH,
            'Q_w': res[winter_mask]['Q_heat_W'].sum()/1000,
            'Q_s': res[shoulder_mask]['Q_heat_W'].sum()/1000,
        })

    df = pd.DataFrame(results)
    df['base_w'] = base_w
    df['base_s'] = base_s
    return df


def calc_nsi(df, param, period='w'):
    sub = df[df['param'] == param]
    Q = sub[f'Q_{period}'].values
    base = sub[f'base_{period}'].iloc[0]

    if param == 'Orientation':
        return (Q.max() - Q.min()) / base / 2.0
    elif param == 'Temp offset':
        slope, *_ = stats.linregress(sub['val'].values, Q)
        return slope / base
    else:
        slope, *_ = stats.linregress(sub['val_norm'].values, Q / base)
        return slope


def calc_sensitivity_table(df):
    params = ['Orientation', 'Internal gains', 'Insulation k', 'Temp offset', 'Absorptance', 'Infiltration']
    rows = []
    for p in params:
        sub = df[df['param'] == p]
        rows.append({
            'Parameter': p,
            'Q_w_min': sub['Q_w'].min(), 'Q_w_max': sub['Q_w'].max(),
            'NSI_w': calc_nsi(df, p, 'w'),
            'Q_s_min': sub['Q_s'].min(), 'Q_s_max': sub['Q_s'].max(),
            'NSI_s': calc_nsi(df, p, 's'),
        })
    tbl = pd.DataFrame(rows)
    tbl['Rank_w'] = tbl['NSI_w'].abs().rank(ascending=False).astype(int)
    tbl['Rank_s'] = tbl['NSI_s'].abs().rank(ascending=False).astype(int)
    return tbl


def print_table_7(tbl):
    print("\n" + "="*90)
    print("TABLE 7: Sensitivity Analysis Results")
    print("="*90)
    print(f"\n{'Parameter':<18} {'Winter Week':^35} {'Shoulder Week':^35}")
    print(f"{'':<18} {'Q Range (kWh)':<15} {'NSI':>8} {'Rank':>6}   {'Q Range (kWh)':<15} {'NSI':>8} {'Rank':>6}")
    print("-"*90)
    for _, r in tbl.iterrows():
        w_rng = f"{r['Q_w_min']:.1f}-{r['Q_w_max']:.1f}"
        s_rng = f"{r['Q_s_min']:.1f}-{r['Q_s_max']:.1f}"
        print(f"  {r['Parameter']:<16} {w_rng:<15} {r['NSI_w']:>+8.3f} {r['Rank_w']:>6}   "
              f"{s_rng:<15} {r['NSI_s']:>+8.3f} {r['Rank_s']:>6}")


def plot_fig7_scatter(df, path):
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()

    params = ['Orientation', 'Internal gains', 'Insulation k', 'Temp offset', 'Absorptance', 'Infiltration']
    xlabels = ['Azimuth (deg)', 'Internal Gains (W)', 'Conductivity (W/mK)',
               'Temp Offset (K)', 'Absorptance', 'Infiltration (ACH)']

    for i, (p, xl) in enumerate(zip(params, xlabels)):
        ax = axes[i]
        sub = df[df['param'] == p]
        x = sub['val'].values
        yw, ys = sub['Q_w'].values, sub['Q_s'].values

        ax.scatter(x, yw, c=COL_WINTER, s=35, edgecolors='white', lw=0.5, label='Winter')
        ax.scatter(x, ys, c=COL_SHOULDER, s=35, edgecolors='white', lw=0.5, label='Shoulder')

        # trend lines
        if p == 'Orientation':
            xc = np.cos(np.deg2rad(x - 180))
            xfit = np.linspace(x.min(), x.max(), 100)
            xcfit = np.cos(np.deg2rad(xfit - 180))
            sw, iw, rw, *_ = stats.linregress(xc, yw)
            ss, Is, rs, *_ = stats.linregress(xc, ys)
            ax.plot(xfit, sw*xcfit + iw, '--', c=COL_WINTER, lw=1, alpha=0.7)
            ax.plot(xfit, ss*xcfit + Is, '--', c=COL_SHOULDER, lw=1, alpha=0.7)
            ax.text(0.05, 0.95, f'R²={rw**2:.3f}', transform=ax.transAxes, fontsize=8, va='top', color=COL_WINTER)
            ax.text(0.05, 0.87, f'R²={rs**2:.3f}', transform=ax.transAxes, fontsize=8, va='top', color=COL_SHOULDER)
        else:
            sw, iw, rw, *_ = stats.linregress(x, yw)
            ss, Is, rs, *_ = stats.linregress(x, ys)
            xfit = np.linspace(x.min(), x.max(), 100)
            ax.plot(xfit, sw*xfit + iw, '--', c=COL_WINTER, lw=1, alpha=0.7)
            ax.plot(xfit, ss*xfit + Is, '--', c=COL_SHOULDER, lw=1, alpha=0.7)
            ax.text(0.05, 0.95, f'slope={sw:.2f}, R²={rw**2:.3f}', transform=ax.transAxes, fontsize=8, va='top', color=COL_WINTER)
            ax.text(0.05, 0.87, f'slope={ss:.2f}, R²={rs**2:.3f}', transform=ax.transAxes, fontsize=8, va='top', color=COL_SHOULDER)

        ax.set_xlabel(xl)
        ax.set_ylabel('Weekly Heating (kWh)')
        ax.set_title(p)
        ax.grid(True, alpha=0.3, lw=0.5)

        # margins
        dx = (x.max() - x.min()) * 0.08
        ax.set_xlim(x.min() - dx, x.max() + dx)
        ally = np.concatenate([yw, ys])
        dy = (ally.max() - ally.min())
        ax.set_ylim(ally.min() - dy*0.15, ally.max() + dy*0.40)

        if i == 0:
            ax.legend(loc='upper right', frameon=True, fontsize=8)

    fig.suptitle('Figure 7: Sensitivity Analysis', fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def plot_fig8_ranking(tbl, path):
    fig, ax = plt.subplots(figsize=(10, 5))

    tbl_sort = tbl.reindex(tbl['NSI_w'].abs().sort_values().index)
    y = np.arange(len(tbl_sort))
    h = 0.35

    bw = ax.barh(y - h/2, tbl_sort['NSI_w'].abs(), h, label='Winter', color=COL_WINTER, edgecolor='white')
    bs = ax.barh(y + h/2, tbl_sort['NSI_s'].abs(), h, label='Shoulder', color=COL_SHOULDER, edgecolor='white')

    ax.set_yticks(y)
    ax.set_yticklabels(tbl_sort['Parameter'])
    ax.set_xlabel('Absolute NSI')
    ax.set_title('Figure 8: Sensitivity Ranking')
    ax.legend(loc='lower right')
    ax.grid(True, axis='x', alpha=0.3, lw=0.5)

    xmax = max(tbl_sort['NSI_w'].abs().max(), tbl_sort['NSI_s'].abs().max())
    ax.set_xlim(0, xmax * 1.25)

    for b in bw:
        ax.text(b.get_width() + 0.01, b.get_y() + b.get_height()/2, f'{b.get_width():.3f}',
                va='center', fontsize=8, color=COL_WINTER)
    for b in bs:
        ax.text(b.get_width() + 0.01, b.get_y() + b.get_height()/2, f'{b.get_width():.3f}',
                va='center', fontsize=8, color=COL_SHOULDER)

    plt.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
