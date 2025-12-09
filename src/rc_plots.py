"""Plotting functions for RC model comparison."""

import numpy as np
import matplotlib.pyplot as plt

COLORS = {
    'lw': '#2563EB',
    'hw': '#DC2626',
    'outdoor': '#1B4D3E',
    'setpoint': '#888888',
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


def plot_rc_comparison(res_lw, res_hw, T_set, output_path='outputs/rc_comparison_week.png'):
    """Plot winter week comparison of lightweight vs heavyweight."""
    week_start = '2021-01-11'
    week_end = '2021-01-18'
    mask_lw = (res_lw['timestamp'] >= week_start) & (res_lw['timestamp'] < week_end)
    mask_hw = (res_hw['timestamp'] >= week_start) & (res_hw['timestamp'] < week_end)

    fig, axes = plt.subplots(4, 1, figsize=(11, 9), sharex=True)
    hours = np.arange(len(res_lw[mask_lw]))

    # Panel 1: Lightweight thermal mass temps
    ax1 = axes[0]
    ax1.plot(hours, res_lw[mask_lw]['T_out_C'], 'k--', lw=1, label='Outdoor')
    ax1.plot(hours, res_lw[mask_lw]['T_C_roof'], lw=1.2, label='Roof')
    ax1.plot(hours, res_lw[mask_lw]['T_C_N'], lw=1.2, label='North')
    ax1.plot(hours, res_lw[mask_lw]['T_C_S'], lw=1.2, label='South')
    ax1.plot(hours, res_lw[mask_lw]['T_C_E'], lw=1.2, label='East')
    ax1.plot(hours, res_lw[mask_lw]['T_C_W'], lw=1.2, label='West')
    ax1.axhline(T_set, color='gray', ls=':', lw=1)
    ax1.set_ylabel('Temperature (°C)')
    ax1.set_ylim(-5, 30)
    ax1.legend(loc='upper right', ncol=3, frameon=True, fancybox=False, fontsize=8)
    ax1.grid(True, alpha=0.3, lw=0.5)
    ax1.set_title('Lightweight (Case 600) - Thermal Mass Temperatures')

    # Panel 2: Heavyweight thermal mass temps
    ax2 = axes[1]
    ax2.plot(hours, res_hw[mask_hw]['T_out_C'], 'k--', lw=1, label='Outdoor')
    ax2.plot(hours, res_hw[mask_hw]['T_C_roof'], lw=1.2, label='Roof')
    ax2.plot(hours, res_hw[mask_hw]['T_C_N'], lw=1.2, label='North')
    ax2.plot(hours, res_hw[mask_hw]['T_C_S'], lw=1.2, label='South')
    ax2.plot(hours, res_hw[mask_hw]['T_C_E'], lw=1.2, label='East')
    ax2.plot(hours, res_hw[mask_hw]['T_C_W'], lw=1.2, label='West')
    ax2.axhline(T_set, color='gray', ls=':', lw=1)
    ax2.set_ylabel('Temperature (°C)')
    ax2.set_ylim(-5, 30)
    ax2.legend(loc='upper right', ncol=3, frameon=True, fancybox=False, fontsize=8)
    ax2.grid(True, alpha=0.3, lw=0.5)
    ax2.set_title('Heavyweight (Case 900) - Thermal Mass Temperatures')

    # Panel 3: Heating load
    ax3 = axes[2]
    ax3.plot(hours, res_lw[mask_lw]['Q_heat_W']/1000, color=COLORS['lw'], lw=1.5,
             label='Lightweight')
    ax3.plot(hours, res_hw[mask_hw]['Q_heat_W']/1000, color=COLORS['hw'], lw=1.5,
             label='Heavyweight')
    ax3.set_ylabel('Heating Load (kW)')
    ax3.set_ylim(0, 2.5)
    ax3.legend(loc='upper right', frameon=True, fancybox=False)
    ax3.grid(True, alpha=0.3, lw=0.5)
    ax3.set_title('Hourly Heating Demand')

    # Panel 4: Difference
    ax4 = axes[3]
    diff = res_hw[mask_hw]['Q_heat_W'].values - res_lw[mask_lw]['Q_heat_W'].values
    ax4.fill_between(hours, diff/1000, 0, where=diff>=0, color=COLORS['hw'], alpha=0.4,
                     label='Heavyweight > Lightweight')
    ax4.fill_between(hours, diff/1000, 0, where=diff<0, color=COLORS['lw'], alpha=0.4,
                     label='Lightweight > Heavyweight')
    ax4.axhline(0, color='k', lw=0.5)
    ax4.set_ylabel('Difference (kW)')
    ax4.set_xlabel('Hour of Week')
    ax4.set_ylim(-0.3, 0.3)
    ax4.legend(loc='upper right', frameon=True, fancybox=False)
    ax4.grid(True, alpha=0.3, lw=0.5)
    ax4.set_title('Heating Load Difference (Heavyweight − Lightweight)')

    # X-axis day labels
    day_ticks = np.arange(0, len(hours), 24)
    day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    ax4.set_xticks(day_ticks)
    ax4.set_xticklabels(day_labels)
    ax4.set_xlim(0, len(hours)-1)

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"\nSaved: {output_path}")
