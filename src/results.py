"""Visualization functions for building energy results."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 10, 'axes.labelsize': 11, 'axes.titlesize': 12,
    'axes.titleweight': 'bold', 'axes.linewidth': 0.8,
    'axes.spines.top': False, 'axes.spines.right': False,
    'legend.fontsize': 9, 'legend.framealpha': 0.95, 'legend.edgecolor': '#CCCCCC',
    'xtick.labelsize': 9, 'ytick.labelsize': 9,
    'figure.dpi': 150, 'savefig.dpi': 300, 'savefig.facecolor': 'white',
})

COLORS = {
    'walls': '#8B4513', 'roof': '#A0522D', 'windows': '#4682B4',
    'inf': '#2F4F4F', 'vent': '#5F9EA0',
    'solar': '#CD853F', 'excess_solar': '#DAA520', 'internal': '#8B0000', 'heating': '#2C3E50',
    'temp': '#1B4D3E', 'irr': '#D35400',
    'S1': '#2C3E50', 'S2': '#566573', 'S3': '#7F8C8D', 'S4': '#95A5A6'
}

SCENARIO_NAMES = {
    'S1': 'S1: Const. 21°C, 0.5 ACH',
    'S2': 'S2: Sched. 21/18°C, 0.5 ACH',
    'S3': 'S3: Const. 21°C, 0.7/0.3 ACH',
    'S4': 'S4: Sched. 21/18°C, 0.7/0.3 ACH'
}


def _save(fig, path):
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)


def print_table_4(results):
    print("\n" + "="*65)
    print("TABLE 4: Annual Heat Flow Breakdown (Base Case S1)")
    print("="*65)

    s1 = results['S1']
    losses = {
        'Walls': s1['Q_walls_W'].sum()/1000, 'Roof': s1['Q_roof_W'].sum()/1000,
        'Windows': s1['Q_win_W'].sum()/1000, 'Infiltration': s1['Q_inf_W'].sum()/1000,
        'Ventilation': s1['Q_vent_W'].sum()/1000,
    }
    gains = {
        'Solar': s1['Q_solar_W'].sum()/1000, 'Internal': s1['Q_int_W'].sum()/1000,
        'Heating': s1['Q_heat_W'].sum()/1000,
    }
    total_loss = sum(losses.values())
    total_gain = sum(gains.values())

    print(f"\n{'HEAT LOSSES':<20} {'kWh':>12} {'%':>10}")
    print("-"*44)
    for k, v in losses.items():
        print(f"  {k:<18} {v:>10.0f} {v/total_loss*100:>9.1f}%")
    print("-"*44)
    print(f"  {'Total Losses':<18} {total_loss:>10.0f} {'100.0%':>10}")

    print(f"\n{'HEAT GAINS':<20} {'kWh':>12} {'%':>10}")
    print("-"*44)
    for k, v in gains.items():
        print(f"  {k:<18} {v:>10.0f} {v/total_gain*100:>9.1f}%")
    print("-"*44)
    print(f"  {'Total Gains':<18} {total_gain:>10.0f} {'100.0%':>10}")


def print_table_5(results, floor_area):
    print("\n" + "="*65)
    print("TABLE 5: Annual Heating Demand Comparison")
    print("="*65)

    base = results['S1']['Q_heat_W'].sum() / 1000
    print(f"\n{'Scenario':<35} {'kWh':>10} {'kWh/m²':>10} {'vs S1':>10}")
    print("-"*67)
    for s in ['S1', 'S2', 'S3', 'S4']:
        kwh = results[s]['Q_heat_W'].sum() / 1000
        intensity = kwh / floor_area
        delta = '—' if s == 'S1' else f"{(kwh-base)/base*100:+.1f}%"
        print(f"  {SCENARIO_NAMES[s]:<33} {kwh:>8.0f} {intensity:>10.1f} {delta:>10}")


def plot_fig2_monthly(results, weather, path):
    fig, ax1 = plt.subplots(figsize=(11, 5.5))
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    x = np.arange(12)

    df = results['S1'].copy()
    df['month'] = df['timestamp'].dt.month
    df['day'] = df['timestamp'].dt.date
    daily = df.groupby('day')['Q_heat_W'].sum() / 1000
    ddf = pd.DataFrame({'day': daily.index, 'kWh': daily.values})
    ddf['month'] = pd.to_datetime(ddf['day']).dt.month
    monthly_avg = ddf.groupby('month')['kWh'].mean()

    wc = weather.copy()
    wc['month'] = wc['timestamp'].dt.month
    temp_mean = wc.groupby('month')['T_out_C'].mean()
    temp_p5 = wc.groupby('month')['T_out_C'].quantile(0.05)
    temp_p95 = wc.groupby('month')['T_out_C'].quantile(0.95)

    ax1.bar(x, monthly_avg.values, 0.7, color=COLORS['S1'], edgecolor='white', linewidth=0.5)
    ax1.set_ylabel('Average Daily Heating Demand (kWh/day)')
    ax1.set_xlabel('Month')
    ax1.set_xticks(x)
    ax1.set_xticklabels(months)
    ax1.set_ylim(0, 55)
    ax1.set_yticks(range(0, 60, 10))

    ax2 = ax1.twinx()
    ax2.fill_between(x, temp_p5.values, temp_p95.values, alpha=0.2, color=COLORS['temp'])
    ax2.plot(x, temp_mean.values, color=COLORS['temp'], lw=1.5, marker='o', ms=4)
    ax2.set_ylabel('Outdoor Temperature (°C)', color=COLORS['temp'])
    ax2.tick_params(axis='y', labelcolor=COLORS['temp'])
    ax2.spines['right'].set_visible(True)
    ax2.spines['right'].set_color(COLORS['temp'])
    ax2.set_ylim(-10, 30)
    ax2.set_yticks(range(-10, 35, 5))

    legend_els = [
        Patch(facecolor=COLORS['S1'], edgecolor='white', label='Avg. Daily Heating'),
        Patch(facecolor=COLORS['temp'], alpha=0.2, label='Temp. 5th–95th %ile'),
        Line2D([0], [0], color=COLORS['temp'], lw=1.5, marker='o', ms=4, label='Mean Temp.')
    ]
    ax1.legend(handles=legend_els, loc='upper right', frameon=True, fancybox=False)
    ax1.set_title('Figure 2: Monthly Heating Profile (Base Case S1, Annual)')
    plt.tight_layout()
    _save(fig, path)


def plot_fig2_2_breakdown(results, weather, path):
    fig, ax1 = plt.subplots(figsize=(11, 5.5))
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    x = np.arange(12)

    df = results['S1'].copy()
    df['month'] = df['timestamp'].dt.month
    df['day'] = df['timestamp'].dt.date

    comps = ['Walls', 'Roof', 'Windows', 'Infiltration', 'Ventilation']
    cols = {'Walls': 'Q_walls_W', 'Roof': 'Q_roof_W', 'Windows': 'Q_win_W',
            'Infiltration': 'Q_inf_W', 'Ventilation': 'Q_vent_W'}
    comp_colors = {'Walls': COLORS['walls'], 'Roof': COLORS['roof'],
                   'Windows': COLORS['windows'], 'Infiltration': COLORS['inf'],
                   'Ventilation': COLORS['vent']}

    monthly = {}
    for c in comps:
        daily = df.groupby('day')[cols[c]].sum() / 1000
        tmp = pd.DataFrame({'day': daily.index, 'kWh': daily.values})
        tmp['month'] = pd.to_datetime(tmp['day']).dt.month
        monthly[c] = tmp.groupby('month')['kWh'].mean().values

    bottom = np.zeros(12)
    bars = []
    for c in comps:
        ax1.bar(x, monthly[c], 0.7, label=c, bottom=bottom,
                color=comp_colors[c], edgecolor='white', linewidth=0.3)
        bars.append((c, monthly[c], bottom.copy()))
        bottom += monthly[c]

    for c, vals, bot in bars:
        for j, (v, b) in enumerate(zip(vals, bot)):
            total = sum(monthly[comp][j] for comp in comps)
            pct = v/total*100
            if pct > 12:
                ax1.text(x[j], b + v/2, f'{pct:.0f}%', ha='center', va='center',
                        fontsize=7, color='white', fontweight='bold')

    ax1.set_ylabel('Average Daily Heat Loss (kWh/day)')
    ax1.set_xlabel('Month')
    ax1.set_xticks(x)
    ax1.set_xticklabels(months)
    ax1.set_ylim(0, 55)
    ax1.set_yticks(range(0, 60, 10))

    wc = weather.copy()
    wc['month'] = wc['timestamp'].dt.month
    temp_mean = wc.groupby('month')['T_out_C'].mean()

    ax2 = ax1.twinx()
    ax2.plot(x, temp_mean.values, color=COLORS['temp'], lw=1.5, marker='o', ms=4)
    ax2.set_ylabel('Temperature (°C)', color=COLORS['temp'])
    ax2.tick_params(axis='y', labelcolor=COLORS['temp'])
    ax2.spines['right'].set_visible(True)
    ax2.spines['right'].set_color(COLORS['temp'])
    ax2.set_ylim(-10, 30)
    ax2.set_yticks(range(-10, 35, 5))

    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    wc['GHI'] = wc['I_dir_Wm2'] + wc['I_dif_Wm2']
    irr_mean = wc.groupby('month')['GHI'].mean()
    ax3.plot(x, irr_mean.values, color=COLORS['irr'], lw=1.5, marker='o', ms=4, linestyle='--')
    ax3.set_ylabel('Irradiance (W/m²)', color=COLORS['irr'])
    ax3.tick_params(axis='y', labelcolor=COLORS['irr'])
    ax3.spines['right'].set_visible(True)
    ax3.spines['right'].set_color(COLORS['irr'])
    ax3.set_ylim(0, 600)
    ax3.set_yticks(range(0, 700, 100))

    h1, _ = ax1.get_legend_handles_labels()
    legend_els = h1 + [
        Line2D([0], [0], color=COLORS['temp'], lw=1.5, marker='o', ms=4, label='Mean Temp.'),
        Line2D([0], [0], color=COLORS['irr'], lw=1.5, marker='o', ms=4, linestyle='--', label='Mean Irradiance'),
    ]
    ax1.legend(handles=legend_els, loc='upper right', frameon=True, fancybox=False, fontsize=8)
    ax1.set_title('Figure 2.2: Average Daily Heat Loss Breakdown (Base Case S1, Annual)')
    plt.tight_layout()
    _save(fig, path)


def plot_fig3_pies(results, path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    s1 = results['S1']

    losses = {
        'Walls': s1['Q_walls_W'].sum()/1000, 'Roof': s1['Q_roof_W'].sum()/1000,
        'Windows': s1['Q_win_W'].sum()/1000, 'Infiltration': s1['Q_inf_W'].sum()/1000,
        'Ventilation': s1['Q_vent_W'].sum()/1000,
    }

    # calculate useful vs excess solar
    tot_loss = sum(losses.values())
    tot_solar = s1['Q_solar_W'].sum()/1000
    internal = s1['Q_int_W'].sum()/1000
    heating = s1['Q_heat_W'].sum()/1000
    useful_solar = max(0, tot_solar - (tot_solar + internal + heating - tot_loss))
    excess_solar = tot_solar - useful_solar

    gains = {
        'Heating': heating, 'Internal': internal,
        'Solar (Useful)': useful_solar, 'Excess Solar': excess_solar,
    }

    loss_colors = [COLORS['walls'], COLORS['roof'], COLORS['windows'], COLORS['inf'], COLORS['vent']]
    gain_colors = [COLORS['heating'], COLORS['internal'], COLORS['solar'], COLORS['excess_solar']]
    total_loss = sum(losses.values())
    total_gain = sum(gains.values())

    w1, _, at1 = ax1.pie(losses.values(), colors=loss_colors, autopct='%1.1f%%',
                          startangle=90, pctdistance=0.75)
    for at in at1:
        at.set_fontsize(10)
        at.set_fontweight('bold')
        at.set_color('white')
    loss_leg = [f'{k}: {v:,.0f} kWh' for k, v in losses.items()]
    ax1.legend(w1, loss_leg, title='Components', loc='center left',
               bbox_to_anchor=(-0.3, 0.5), frameon=True, fancybox=False)
    ax1.set_title(f'Heat Losses\nTotal: {total_loss:,.0f} kWh', fontweight='bold', fontsize=12)

    # pie only shows useful gains (exclude excess solar)
    pie_gains = {k: v for k, v in gains.items() if k != 'Excess Solar'}
    pie_colors = [COLORS['heating'], COLORS['internal'], COLORS['solar']]
    pie_total = sum(pie_gains.values())

    w2, _, at2 = ax2.pie(pie_gains.values(), colors=pie_colors, autopct='%1.1f%%',
                          startangle=90, pctdistance=0.75)
    for at in at2:
        at.set_fontsize(10)
        at.set_fontweight('bold')
        at.set_color('white')

    # legend includes excess solar
    gain_leg = [f'{k}: {v:,.0f} kWh' for k, v in gains.items()]
    leg_handles = list(w2) + [Patch(facecolor=COLORS['excess_solar'], edgecolor='none')]
    ax2.legend(leg_handles, gain_leg, title='Components', loc='center right',
               bbox_to_anchor=(1.35, 0.5), frameon=True, fancybox=False)
    ax2.set_title(f'Heat Gains\nTotal: {pie_total:,.0f} kWh', fontweight='bold', fontsize=12)

    fig.suptitle('Figure 3: Annual Heat Flow Breakdown (Base Case S1)',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    _save(fig, path)


def plot_fig4_stacked(results, path):
    fig, ax = plt.subplots(figsize=(10, 6))
    scenarios = ['S1', 'S2', 'S3', 'S4']
    comps = ['Walls', 'Roof', 'Windows', 'Infiltration', 'Ventilation']
    comp_colors = {'Walls': COLORS['walls'], 'Roof': COLORS['roof'],
                   'Windows': COLORS['windows'], 'Infiltration': COLORS['inf'],
                   'Ventilation': COLORS['vent']}

    xlabels = ['S1: Base Case\nConst. 21°C\n0.5 ACH',
               'S2: Setback\nSched. 21/18°C\n0.5 ACH',
               'S3: Variable Vent\nConst. 21°C\n0.7/0.3 ACH',
               'S4: Combined\nSched. 21/18°C\n0.7/0.3 ACH']

    data = {}
    for s in scenarios:
        df = results[s]
        data[s] = {
            'Walls': df['Q_walls_W'].sum()/1000, 'Roof': df['Q_roof_W'].sum()/1000,
            'Windows': df['Q_win_W'].sum()/1000, 'Infiltration': df['Q_inf_W'].sum()/1000,
            'Ventilation': df['Q_vent_W'].sum()/1000,
        }

    x = np.arange(4)
    bottom = np.zeros(4)
    bars = []
    for c in comps:
        vals = [data[s][c] for s in scenarios]
        ax.bar(x, vals, 0.45, label=c, bottom=bottom, color=comp_colors[c], edgecolor='none')
        bars.append((c, vals, bottom.copy()))
        bottom += vals

    for c, vals, bot in bars:
        for j, (v, b) in enumerate(zip(vals, bot)):
            total = sum(data[scenarios[j]].values())
            pct = v/total*100
            if pct > 8:
                ax.text(x[j], b + v/2, f'{v:,.0f}\n({pct:.0f}%)', ha='center', va='center',
                        fontsize=9, color='white', fontweight='bold')
            elif pct > 5:
                ax.text(x[j], b + v/2, f'({pct:.0f}%)', ha='center', va='center',
                        fontsize=9, color='white', fontweight='bold')

    for j, s in enumerate(scenarios):
        total = sum(data[s].values())
        ax.text(x[j], total + 150, f'{total:,.0f}', ha='center', va='bottom',
                fontsize=9, fontweight='bold', color='black')

    ax.set_ylabel('Annual Heat Loss (kWh)')
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=9, linespacing=1.2)
    ax.set_ylim(0, 22000)
    ax.set_yticks(range(0, 24000, 2500))
    ax.grid(True, axis='y', alpha=0.3, linewidth=0.5)
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), frameon=True, fancybox=False)
    ax.set_title('Figure 4: Annual Heat Loss Breakdown Comparison')
    plt.tight_layout()
    _save(fig, path)


def plot_fig4_2_gains(results, path):
    fig, ax = plt.subplots(figsize=(10, 6))
    scenarios = ['S1', 'S2', 'S3', 'S4']
    comps = ['Heating', 'Internal', 'Solar (Useful)', 'Excess Solar']
    comp_colors = {'Solar (Useful)': COLORS['solar'], 'Excess Solar': COLORS['excess_solar'],
                   'Internal': COLORS['internal'], 'Heating': COLORS['heating']}

    xlabels = ['S1: Base Case\nConst. 21°C\n0.5 ACH',
               'S2: Setback\nSched. 21/18°C\n0.5 ACH',
               'S3: Variable Vent\nConst. 21°C\n0.7/0.3 ACH',
               'S4: Combined\nSched. 21/18°C\n0.7/0.3 ACH']

    data = {}
    for s in scenarios:
        df = results[s]
        tot_loss = (df['Q_walls_W'].sum() + df['Q_roof_W'].sum() + df['Q_win_W'].sum() +
                    df['Q_inf_W'].sum() + df['Q_vent_W'].sum()) / 1000
        tot_solar = df['Q_solar_W'].sum() / 1000
        internal = df['Q_int_W'].sum() / 1000
        heating = df['Q_heat_W'].sum() / 1000

        useful_solar = min(tot_solar, tot_loss - internal - heating)
        useful_solar = max(0, tot_solar - (tot_solar + internal + heating - tot_loss))
        excess = tot_solar - useful_solar

        data[s] = {'Heating': heating, 'Internal': internal,
                   'Solar (Useful)': useful_solar, 'Excess Solar': excess}

    x = np.arange(4)
    bottom = np.zeros(4)
    bars = []
    for c in comps:
        vals = [data[s][c] for s in scenarios]
        ax.bar(x, vals, 0.45, label=c, bottom=bottom, color=comp_colors[c], edgecolor='none')
        bars.append((c, vals, bottom.copy()))
        bottom += vals

    for c, vals, bot in bars:
        for j, (v, b) in enumerate(zip(vals, bot)):
            total = sum(data[scenarios[j]].values())
            pct = v/total*100
            if c == 'Heating':
                if pct > 8:
                    ax.text(x[j], b + v/2, f'{v:,.0f} kWh\n({pct:.0f}%)', ha='center', va='center',
                            fontsize=9, color='white', fontweight='bold')
                elif pct > 5:
                    ax.text(x[j], b + v/2, f'({pct:.0f}%)', ha='center', va='center',
                            fontsize=9, color='white', fontweight='bold')
            else:
                if pct > 8:
                    ax.text(x[j], b + v/2, f'{v:,.0f}\n({pct:.0f}%)', ha='center', va='center',
                            fontsize=9, color='white', fontweight='bold')
                elif pct > 5:
                    ax.text(x[j], b + v/2, f'({pct:.0f}%)', ha='center', va='center',
                            fontsize=9, color='white', fontweight='bold')

    # total annotation (excluding excess solar)
    for j, s in enumerate(scenarios):
        useful_tot = data[s]['Heating'] + data[s]['Internal'] + data[s]['Solar (Useful)']
        ax.text(x[j], useful_tot + 150, f'{useful_tot:,.0f} kWh', ha='center', va='bottom',
                fontsize=9, fontweight='bold', color='black')

    # heating comparison vs S1
    base_heat = data['S1']['Heating']
    for j, s in enumerate(scenarios):
        if s == 'S1':
            continue
        heat = data[s]['Heating']
        pct_chg = (heat - base_heat) / base_heat * 100
        mid = data[s]['Heating'] / 2
        if pct_chg < 0:
            lbl = f'▼ {abs(pct_chg):.1f}%'
            clr = '#90EE90'
        else:
            lbl = f'▲ +{pct_chg:.1f}%'
            clr = '#FF6B6B'
        ax.text(x[j], mid - 900, lbl, ha='center', va='center',
                fontsize=10, fontweight='bold', color=clr)

    ax.set_ylabel('Annual Heat Gain (kWh)')
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=9, linespacing=1.2)
    ax.set_ylim(0, 22000)
    ax.set_yticks(range(0, 24000, 2500))
    ax.grid(True, axis='y', alpha=0.3, linewidth=0.5)
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), frameon=True, fancybox=False)
    ax.set_title('Figure 4.2: Annual Heat Gain Breakdown Comparison')
    plt.tight_layout()
    _save(fig, path)


def plot_fig5_winter(results, winter_mask, weather, path):
    _plot_hourly(results, winter_mask, weather,
                 'Figure 5: Average Hourly Heating Load (Winter Week: 8–14 January)', path)


def plot_fig6_shoulder(results, shoulder_mask, weather, path):
    _plot_hourly(results, shoulder_mask, weather,
                 'Figure 6: Average Hourly Heating Load (Shoulder Week: 7–13 October)', path)


def _plot_hourly(results, mask, weather, title, path):
    fig, ax1 = plt.subplots(figsize=(11, 5.5))

    hrs = np.arange(24)
    hrs_disp = np.arange(1, 25)
    styles = {'S1': '-', 'S2': '--', 'S3': '-.', 'S4': ':'}
    widths = {'S1': 1.8, 'S2': 1.5, 'S3': 1.5, 'S4': 1.5}

    for s in ['S1', 'S2', 'S3', 'S4']:
        df = results[s][mask].copy()
        df['hour'] = df['timestamp'].dt.hour
        hourly = df.groupby('hour')['Q_heat_W'].mean() / 1000
        hourly = hourly.reindex(hrs, fill_value=0)
        ax1.plot(hrs_disp, hourly.values, color=COLORS[s], linestyle=styles[s],
                linewidth=widths[s], marker='o', markersize=4, label=SCENARIO_NAMES[s])

    ax1.axvspan(0.5, 7.5, alpha=0.08, color='#1C3144')
    ax1.axvspan(23.5, 24.5, alpha=0.08, color='#1C3144')

    ax1.set_ylabel('Heating Load (kW)')
    ax1.set_xlabel('Hour of Day')
    ax1.set_xticks(range(1, 25))
    ax1.set_xticklabels([str(h) for h in range(1, 25)], fontsize=8)
    ax1.set_xlim(0.5, 24.5)
    ax1.set_ylim(0, 3.0)
    ax1.set_yticks([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    ax1.grid(True, alpha=0.3, linewidth=0.5)

    ww = weather[mask].copy()
    ww['hour'] = ww['timestamp'].dt.hour
    temp = ww.groupby('hour')['T_out_C'].mean()
    temp = temp.reindex(hrs, fill_value=temp.mean())

    ax2 = ax1.twinx()
    ax2.plot(hrs_disp, temp.values, color=COLORS['temp'], lw=1.5, marker='o', ms=3,
             linestyle='--', label='Outdoor Temp.')
    ax2.set_ylabel('Temperature (°C)', color=COLORS['temp'])
    ax2.tick_params(axis='y', labelcolor=COLORS['temp'])
    ax2.spines['right'].set_visible(True)
    ax2.spines['right'].set_color(COLORS['temp'])
    ax2.set_ylim(-10, 30)
    ax2.set_yticks(range(-10, 35, 5))

    ww['GHI'] = ww['I_dir_Wm2'] + ww['I_dif_Wm2']
    irr = ww.groupby('hour')['GHI'].mean()
    irr = irr.reindex(hrs, fill_value=0)

    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    ax3.plot(hrs_disp, irr.values, color=COLORS['irr'], lw=1.5, marker='o', ms=3,
             linestyle=':', label='Irradiance')
    ax3.set_ylabel('Irradiance (W/m²)', color=COLORS['irr'])
    ax3.tick_params(axis='y', labelcolor=COLORS['irr'])
    ax3.spines['right'].set_visible(True)
    ax3.spines['right'].set_color(COLORS['irr'])
    ax3.set_ylim(0, 600)
    ax3.set_yticks(range(0, 700, 100))

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    h3, l3 = ax3.get_legend_handles_labels()
    night = Patch(facecolor='#1C3144', alpha=0.08, label='Night (setback)')
    ax1.legend(h1 + h2 + h3 + [night], l1 + l2 + l3 + ['Night (setback)'],
               loc='upper right', frameon=True, fancybox=False, fontsize=8)

    ax1.set_title(title)
    plt.tight_layout()
    _save(fig, path)
