import matplotlib.pyplot as plt
import numpy as np


def plot_monthly_temperature(weather):
    """Monthly average temperature - academic style"""
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))

    monthly_temp = weather.groupby(weather['timestamp'].dt.month)['T_out_C'].mean()
    months = monthly_temp.index
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Outdoor temperature: dark blue-gray with shaded area
    ax.fill_between(months, monthly_temp.values, alpha=0.15, color='#2E4053', zorder=1)
    ax.plot(months, monthly_temp.values, marker='o', color='#2E4053',
            linewidth=2.0, markersize=5, markerfacecolor='#2E4053',
            markeredgecolor='#2E4053', label='Outdoor Air', zorder=3)

    # Ground temperature (if available)
    if 'T_ground_C' in weather.columns:
        monthly_ground = weather.groupby(weather['timestamp'].dt.month)['T_ground_C'].mean()
        ax.fill_between(months, monthly_ground.values, alpha=0.15, color='#7B7D7D', zorder=1)
        ax.plot(months, monthly_ground.values, marker='s', color='#7B7D7D',
                linewidth=2.0, markersize=5, markerfacecolor='#7B7D7D',
                markeredgecolor='#7B7D7D', label='Ground (2m depth)', zorder=3)

    ax.set_xlabel('Month', fontsize=10)
    ax.set_ylabel('Temperature (°C)', fontsize=10)
    ax.set_title('Monthly Average Temperature', fontsize=11, pad=12)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names, fontsize=8, rotation=45, ha='right')
    ax.tick_params(axis='both', labelsize=9)

    # Professional legend
    ax.legend(loc='upper left', frameon=True, fontsize=9, framealpha=1.0,
              facecolor='white', edgecolor='#666666', fancybox=False)

    # Professional grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='gray', zorder=0)
    ax.set_axisbelow(True)

    # Clean spines
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('#666666')
        ax.spines[spine].set_linewidth(0.8)

    plt.tight_layout()
    return fig


def plot_monthly_solar(weather):
    """Monthly average solar radiation (direct and diffuse) - academic style"""
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))

    if 'I_dir_Wm2' not in weather.columns or 'I_dif_Wm2' not in weather.columns:
        ax.text(0.5, 0.5, 'Solar radiation data not available', ha='center', va='center')
        return fig

    monthly_dir = weather.groupby(weather['timestamp'].dt.month)['I_dir_Wm2'].mean()
    monthly_dif = weather.groupby(weather['timestamp'].dt.month)['I_dif_Wm2'].mean()
    months = monthly_dir.index
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Professional colors with shaded areas
    ax.fill_between(months, monthly_dir.values, alpha=0.15, color='#D35400', zorder=1)
    ax.plot(months, monthly_dir.values, marker='o', color='#D35400',
            linewidth=2.0, markersize=5, markerfacecolor='#D35400',
            markeredgecolor='#D35400', label='Direct Normal', zorder=3)

    ax.fill_between(months, monthly_dif.values, alpha=0.15, color='#2874A6', zorder=1)
    ax.plot(months, monthly_dif.values, marker='s', color='#2874A6',
            linewidth=2.0, markersize=5, markerfacecolor='#2874A6',
            markeredgecolor='#2874A6', label='Diffuse Horizontal', zorder=3)

    ax.set_xlabel('Month', fontsize=10)
    ax.set_ylabel('Solar Irradiance (W/m²)', fontsize=10)
    ax.set_title('Monthly Average Solar Radiation Components', fontsize=11, pad=12)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names, fontsize=8, rotation=45, ha='right')
    ax.tick_params(axis='both', labelsize=9)

    # Professional legend
    ax.legend(loc='upper left', frameon=True, fontsize=9, framealpha=1.0,
              facecolor='white', edgecolor='#666666', fancybox=False)

    # Professional grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='gray', zorder=0)
    ax.set_axisbelow(True)

    # Clean spines
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('#666666')
        ax.spines[spine].set_linewidth(0.8)

    plt.tight_layout()
    return fig


def plot_monthly_solar_elevation(weather):
    """Monthly maximum solar elevation - academic style"""
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))

    if 'theta_s_deg' not in weather.columns:
        ax.text(0.5, 0.5, 'Solar elevation data not available', ha='center', va='center')
        return fig

    monthly_solar_elev = weather.groupby(weather['timestamp'].dt.month).apply(
        lambda x: (90 - x['theta_s_deg']).max()
    )
    months = monthly_solar_elev.index
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Professional color: amber/golden for sun with shaded area
    ax.fill_between(months, monthly_solar_elev.values, alpha=0.15, color='#D68910', zorder=1)
    ax.plot(months, monthly_solar_elev.values, marker='^', color='#D68910',
            linewidth=2.0, markersize=5, markerfacecolor='#D68910',
            markeredgecolor='#D68910', zorder=3)

    ax.set_xlabel('Month', fontsize=10)
    ax.set_ylabel('Solar Elevation Angle (°)', fontsize=10)
    ax.set_title('Monthly Maximum Solar Elevation', fontsize=11, pad=12)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names, fontsize=8, rotation=45, ha='right')
    ax.tick_params(axis='both', labelsize=9)

    # Professional grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='gray', zorder=0)
    ax.set_axisbelow(True)

    # Clean spines
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('#666666')
        ax.spines[spine].set_linewidth(0.8)

    plt.tight_layout()
    return fig


def plot_temp_distribution(weather, design_day_cold=None, design_day_hot=None, temp_04=None, temp_996=None):
    """Temperature distribution with design conditions - academic style"""
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))

    temps = weather['T_out_C']
    heat_design = np.percentile(temps, 0.4) if temp_04 is None else temp_04
    cool_design = np.percentile(temps, 99.6) if temp_996 is None else temp_996

    # Professional histogram with subtle color
    n, bins, patches = ax.hist(temps, bins=50, color='#5D6D7E',
                               edgecolor='white', linewidth=0.5, alpha=0.65)

    # Design condition lines - SWAPPED: Heating=Red, Cooling=Blue
    ax.axvline(heat_design, color='#C0392B', linestyle='--', linewidth=2.5,
               label=f'Heating Design: {heat_design:.1f}°C (0.4%)', zorder=5)
    ax.axvline(cool_design, color='#2874A6', linestyle='--', linewidth=2.5,
               label=f'Cooling Design: {cool_design:.1f}°C (99.6%)', zorder=5)

    ax.set_xlabel('Temperature (°C)', fontsize=10)
    ax.set_ylabel('Frequency (hours)', fontsize=10)
    ax.set_title('Temperature Distribution & Design Conditions', fontsize=11, pad=12)
    ax.tick_params(axis='both', labelsize=9)

    # Professional legend
    ax.legend(loc='upper right', frameon=True, fontsize=9, framealpha=1.0,
              facecolor='white', edgecolor='#666666', fancybox=False)

    # Professional grid
    ax.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.5, color='gray', zorder=0)
    ax.set_axisbelow(True)

    # Clean spines
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('#666666')
        ax.spines[spine].set_linewidth(0.8)

    # Add statistics text box (without "Temperature Statistics:" label) - opaque so lines don't show through
    stats_text = f"Min: {temps.min():.1f}°C\n"
    stats_text += f"Max: {temps.max():.1f}°C\n"
    stats_text += f"Mean: {temps.mean():.1f}°C\n"
    stats_text += f"Median: {temps.median():.1f}°C\n"

    if design_day_cold is not None and design_day_hot is not None:
        stats_text += f"\nDesign Days:\n"
        stats_text += f"  Heating: {design_day_cold}\n"
        stats_text += f"  Cooling: {design_day_hot}"

    plt.tight_layout()
    return fig


def plot_peak_heating_breakdown(results, planes, air, weather, T_heat):
    """Detailed breakdown of peak heating load by building elements"""
    from config import RHO_AIR, CP_AIR

    # Find peak heating hour
    peak_idx = results['Q_heat_W'].idxmax()
    peak_load_kW = results.loc[peak_idx, 'Q_heat_W'] / 1000
    T_out_peak = results.loc[peak_idx, 'T_out_C']

    # Calculate heat loss for each building element type at peak hour
    losses = {}

    # Group planes by type
    walls_ag = []  # Above-ground walls
    roofs = []
    windows = []
    walls_ug = []  # Underground walls
    floors = []

    for p in planes:
        if p.is_opaque():
            if p.ground_contact:
                if p.tilt_deg == 90:
                    walls_ug.append(p)
                else:  # floor
                    floors.append(p)
            else:
                if p.tilt_deg == 90:
                    walls_ag.append(p)
                else:  # roof
                    roofs.append(p)
        elif p.is_window():
            windows.append(p)

    # Get boundary temperatures at peak hour
    if 'T_ground_C' in weather.columns:
        T_ground = weather.iloc[peak_idx]['T_ground_C']
    else:
        T_ground = T_out_peak

    # Calculate losses for each category
    losses['Walls (Above Ground)'] = sum(p.U * p.area_m2 * abs(T_out_peak - T_heat) for p in walls_ag) / 1000
    losses['Roofs'] = sum(p.U * p.area_m2 * abs(T_out_peak - T_heat) for p in roofs) / 1000
    losses['Windows'] = sum(p.U * p.area_m2 * abs(T_out_peak - T_heat) for p in windows) / 1000
    losses['Basement Walls'] = sum(p.U * p.area_m2 * abs(T_ground - T_heat) for p in walls_ug) / 1000
    losses['Floor Slab'] = sum(p.U * p.area_m2 * abs(T_ground - T_heat) for p in floors) / 1000

    # Ventilation and infiltration
    V_inf_m3s = air.ACH_infiltration_h * air.V_zone_m3 / 3600.0
    losses['Ventilation (HRV)'] = abs(RHO_AIR * CP_AIR * air.Vdot_vent_m3s * (1.0 - air.eta_HRV) * (T_out_peak - T_heat)) / 1000
    losses['Infiltration'] = abs(RHO_AIR * CP_AIR * V_inf_m3s * (T_out_peak - T_heat)) / 1000

    # Create pie chart
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    # Filter out zero values and prepare data
    filtered_losses = {k: v for k, v in losses.items() if v > 0.1}

    # Professional academic color palette with high contrast and distinction
    color_map = {
        'Walls (Above Ground)': '#8B0000',  # Dark red - largest envelope component
        'Roofs': '#D35400',                  # Dark orange - distinct from walls
        'Windows': '#2874A6',                # Professional blue - glazing
        'Basement Walls': '#566573',         # Medium gray - underground
        'Floor Slab': '#34495E',             # Dark blue-gray - foundation
        'Ventilation (HRV)': '#16A085',      # Teal - mechanical ventilation
        'Infiltration': '#AF7AC5'            # Light purple - air leakage (distinct from ventilation)
    }

    # Sort by size
    sorted_items = sorted(filtered_losses.items(), key=lambda x: x[1], reverse=True)

    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    percentages = [v/peak_load_kW * 100 for v in values]

    # Get colors in sorted order
    colors = [color_map[label] for label in labels]

    # Create pie
    wedges, texts, autotexts = ax.pie(values, labels=None, colors=colors[:len(values)],
                                       autopct='%1.1f%%', startangle=90,
                                       wedgeprops={'edgecolor': 'white', 'linewidth': 2})

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
        autotext.set_weight('bold')

    # Create detailed legend with kW values
    legend_labels = [f'{label}: {value:.1f} kW ({pct:.1f}%)'
                     for label, value, pct in zip(labels, values, percentages)]

    ax.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
              fontsize=10, frameon=True, facecolor='white', edgecolor='#666666')

    # Title with peak info
    timestamp = results.loc[peak_idx, 'timestamp']
    title = f'Peak Heating Load Breakdown\n'
    title += f'Total: {peak_load_kW:.1f} kW at {timestamp}\n'
    title += f'Outdoor Temperature: {T_out_peak:.1f}°C'
    ax.set_title(title, fontsize=13, fontweight='bold', pad=20)

    plt.tight_layout()
    return fig


def plot_temp_overview(weather, design_day_cold=None, design_day_hot=None, temp_04=None, temp_996=None):
    """
    Create a 2-panel overview of weather data:
    - Top: Monthly averages (3 separate clean subplots)
    - Bottom: Temperature distribution with design conditions
    """
    # Create figure with custom layout: 3 subplots on top row, 1 on bottom (50% height)
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 0.7], hspace=0.35, wspace=0.25)

    # Top row: 3 subplots for monthly data
    ax_temp = fig.add_subplot(gs[0, 0])
    ax_ir = fig.add_subplot(gs[0, 1])
    ax_solar = fig.add_subplot(gs[0, 2])

    # Bottom row: 1 subplot spanning all columns
    ax_dist = fig.add_subplot(gs[1, :])

    # === TOP ROW: 3 SEPARATE MONTHLY OVERVIEW PLOTS ===

    # Monthly aggregations
    monthly_temp = weather.groupby(weather['timestamp'].dt.month)['T_out_C'].mean()
    monthly_ir = weather.groupby(weather['timestamp'].dt.month)['I_LW_Wm2'].mean() if 'I_LW_Wm2' in weather.columns else None
    monthly_solar_elev = weather.groupby(weather['timestamp'].dt.month).apply(
        lambda x: (90 - x['theta_s_deg']).max() if 'theta_s_deg' in x.columns else 0
    )

    months = monthly_temp.index
    month_names = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']

    # 1. TEMPERATURE
    ax_temp.plot(months, monthly_temp.values, marker='o', color='#2C3E50',
                 linewidth=2.5, markersize=7, markeredgecolor='white', markeredgewidth=1.5, zorder=3)
    ax_temp.fill_between(months, monthly_temp.values, alpha=0.2, color='#2C3E50', zorder=1)
    ax_temp.set_ylabel('Temperature (°C)', fontsize=10, fontweight='bold')
    ax_temp.set_title('Monthly Avg Temperature', fontsize=11, fontweight='bold', pad=10)
    ax_temp.set_xticks(range(1, 13))
    ax_temp.set_xticklabels(month_names, fontsize=9)
    ax_temp.grid(True, alpha=0.25, linestyle='--', linewidth=0.5, zorder=0)
    ax_temp.spines['top'].set_visible(False)
    ax_temp.spines['right'].set_visible(False)
    # Add value labels on peaks
    ax_temp.text(monthly_temp.idxmax(), monthly_temp.max(), f'{monthly_temp.max():.1f}°C',
                ha='center', va='bottom', fontsize=8, fontweight='bold', color='#2C3E50')
    ax_temp.text(monthly_temp.idxmin(), monthly_temp.min(), f'{monthly_temp.min():.1f}°C',
                ha='center', va='top', fontsize=8, fontweight='bold', color='#2C3E50')

    # 2. INFRARED RADIATION
    if monthly_ir is not None:
        ax_ir.plot(months, monthly_ir.values, marker='s', color='#E67E22',
                   linewidth=2.5, markersize=7, markeredgecolor='white', markeredgewidth=1.5, zorder=3)
        ax_ir.fill_between(months, monthly_ir.values, alpha=0.2, color='#E67E22', zorder=1)
        ax_ir.set_ylabel('IR Radiation (W/m²)', fontsize=10, fontweight='bold')
        ax_ir.set_title('Monthly Avg IR Radiation', fontsize=11, fontweight='bold', pad=10)
        ax_ir.set_xticks(range(1, 13))
        ax_ir.set_xticklabels(month_names, fontsize=9)
        ax_ir.grid(True, alpha=0.25, linestyle='--', linewidth=0.5, zorder=0)
        ax_ir.spines['top'].set_visible(False)
        ax_ir.spines['right'].set_visible(False)
        # Add value labels on peaks
        ax_ir.text(monthly_ir.idxmax(), monthly_ir.max(), f'{monthly_ir.max():.0f}',
                  ha='center', va='bottom', fontsize=8, fontweight='bold', color='#E67E22')
        ax_ir.text(monthly_ir.idxmin(), monthly_ir.min(), f'{monthly_ir.min():.0f}',
                  ha='center', va='top', fontsize=8, fontweight='bold', color='#E67E22')

    # 3. SOLAR ELEVATION
    ax_solar.plot(months, monthly_solar_elev.values, marker='^', color='#F39C12',
                  linewidth=2.5, markersize=7, markeredgecolor='white', markeredgewidth=1.5, zorder=3)
    ax_solar.fill_between(months, monthly_solar_elev.values, alpha=0.2, color='#F39C12', zorder=1)
    ax_solar.set_ylabel('Solar Elevation (°)', fontsize=10, fontweight='bold')
    ax_solar.set_title('Monthly Max Solar Elevation', fontsize=11, fontweight='bold', pad=10)
    ax_solar.set_xticks(range(1, 13))
    ax_solar.set_xticklabels(month_names, fontsize=9)
    ax_solar.grid(True, alpha=0.25, linestyle='--', linewidth=0.5, zorder=0)
    ax_solar.spines['top'].set_visible(False)
    ax_solar.spines['right'].set_visible(False)
    # Add value labels on peaks
    ax_solar.text(monthly_solar_elev.idxmax(), monthly_solar_elev.max(), f'{monthly_solar_elev.max():.1f}°',
                 ha='center', va='bottom', fontsize=8, fontweight='bold', color='#F39C12')
    ax_solar.text(monthly_solar_elev.idxmin(), monthly_solar_elev.min(), f'{monthly_solar_elev.min():.1f}°',
                 ha='center', va='top', fontsize=8, fontweight='bold', color='#F39C12')

    # === BOTTOM: TEMPERATURE DISTRIBUTION WITH DESIGN CONDITIONS ===

    temps = weather['T_out_C']
    heat_design = np.percentile(temps, 0.4) if temp_04 is None else temp_04
    cool_design = np.percentile(temps, 99.6) if temp_996 is None else temp_996

    # Histogram
    n, bins, patches = ax_dist.hist(temps, bins=50, color='#34495E',
                                     edgecolor='white', linewidth=0.8, alpha=0.7)

    # Design condition lines
    ax_dist.axvline(heat_design, color='#3498DB', linestyle='--', linewidth=3,
                    label=f'Heating Design: {heat_design:.1f}°C (0.4%)', zorder=5)
    ax_dist.axvline(cool_design, color='#E74C3C', linestyle='--', linewidth=3,
                    label=f'Cooling Design: {cool_design:.1f}°C (99.6%)', zorder=5)

    ax_dist.set_xlabel('Temperature (°C)', fontsize=11, fontweight='bold')
    ax_dist.set_ylabel('Frequency (hours)', fontsize=11, fontweight='bold')
    ax_dist.set_title('Temperature Distribution & Design Conditions', fontsize=13, fontweight='bold', pad=15)
    ax_dist.legend(loc='upper right', frameon=True, fontsize=10)
    ax_dist.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.5)
    ax_dist.spines['top'].set_visible(False)
    ax_dist.spines['right'].set_visible(False)

    # Add statistics text box
    stats_text = f"Temperature Statistics:\n"
    stats_text += f"  Min: {temps.min():.1f}°C\n"
    stats_text += f"  Max: {temps.max():.1f}°C\n"
    stats_text += f"  Mean: {temps.mean():.1f}°C\n"
    stats_text += f"  Median: {temps.median():.1f}°C\n"

    if design_day_cold is not None and design_day_hot is not None:
        stats_text += f"\nDesign Days:\n"
        stats_text += f"  Heating: {design_day_cold}\n"
        stats_text += f"  Cooling: {design_day_hot}"

    ax_dist.text(0.02, 0.98, stats_text, transform=ax_dist.transAxes,
                 fontsize=9, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()
    return fig


def plot_solar_radiation(weather):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # Direct radiation over year
    axes[0, 0].plot(weather['timestamp'], weather['I_dir_Wm2'],
                    color='#E67E22', linewidth=0.8, alpha=0.7)
    axes[0, 0].set_ylabel('Irradiance (W/m²)')
    axes[0, 0].set_title('Direct Normal Radiation')
    axes[0, 0].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[0, 0].spines['top'].set_visible(False)
    axes[0, 0].spines['right'].set_visible(False)

    # Add y-axis padding and info
    dir_max = weather['I_dir_Wm2'].max()
    dir_avg = weather['I_dir_Wm2'].mean()
    axes[0, 0].set_ylim(0, dir_max * 1.15)
    axes[0, 0].text(0.02, 0.98, f'Max: {dir_max:.0f} W/m²\nAvg: {dir_avg:.0f} W/m²',
                    transform=axes[0, 0].transAxes, fontsize=9,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    # Diffuse radiation over year
    axes[0, 1].plot(weather['timestamp'], weather['I_dif_Wm2'],
                    color='#95A5A6', linewidth=0.8, alpha=0.7)
    axes[0, 1].set_ylabel('Irradiance (W/m²)')
    axes[0, 1].set_title('Diffuse Horizontal Radiation')
    axes[0, 1].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[0, 1].spines['top'].set_visible(False)
    axes[0, 1].spines['right'].set_visible(False)

    # Add y-axis padding and info
    dif_max = weather['I_dif_Wm2'].max()
    dif_avg = weather['I_dif_Wm2'].mean()
    axes[0, 1].set_ylim(0, dif_max * 1.15)
    axes[0, 1].text(0.02, 0.98, f'Max: {dif_max:.0f} W/m²\nAvg: {dif_avg:.0f} W/m²',
                    transform=axes[0, 1].transAxes, fontsize=9,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    # Infrared radiation over year
    axes[1, 0].plot(weather['timestamp'], weather['I_LW_Wm2'],
                    color='#8E44AD', linewidth=0.8, alpha=0.7)
    axes[1, 0].set_ylabel('Irradiance (W/m²)')
    axes[1, 0].set_title('Longwave Infrared Radiation')
    axes[1, 0].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[1, 0].spines['top'].set_visible(False)
    axes[1, 0].spines['right'].set_visible(False)

    # Add y-axis padding and info
    ir_min = weather['I_LW_Wm2'].min()
    ir_max = weather['I_LW_Wm2'].max()
    ir_avg = weather['I_LW_Wm2'].mean()
    ir_range = ir_max - ir_min
    axes[1, 0].set_ylim(ir_min - ir_range * 0.1, ir_max + ir_range * 0.15)
    axes[1, 0].text(0.02, 0.98, f'Max: {ir_max:.0f} W/m²\nAvg: {ir_avg:.0f} W/m²\nMin: {ir_min:.0f} W/m²',
                    transform=axes[1, 0].transAxes, fontsize=9,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    # Monthly average solar
    monthly_dir = weather.groupby(weather['timestamp'].dt.month)['I_dir_Wm2'].mean()
    monthly_dif = weather.groupby(weather['timestamp'].dt.month)['I_dif_Wm2'].mean()
    monthly_ir = weather.groupby(weather['timestamp'].dt.month)['I_LW_Wm2'].mean()

    x = np.arange(len(monthly_dir.index))
    width = 0.35

    axes[1, 1].bar(x - width/2, monthly_dir.values, width, color='#E67E22', alpha=0.8, label='Direct')
    axes[1, 1].bar(x + width/2, monthly_dif.values, width, color='#95A5A6', alpha=0.8, label='Diffuse')
    axes[1, 1].set_xlabel('Month')
    axes[1, 1].set_ylabel('Irradiance (W/m²)')
    axes[1, 1].set_title('Monthly Average Solar Radiation')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(monthly_dir.index)
    axes[1, 1].legend(frameon=False)
    axes[1, 1].grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.5)
    axes[1, 1].spines['top'].set_visible(False)
    axes[1, 1].spines['right'].set_visible(False)

    plt.tight_layout()
    return fig


def plot_sun_path(weather):
    fig, ax = plt.subplots(figsize=(12, 5))

    # Solar elevation throughout year
    solar_elev = 90 - weather['theta_s_deg']
    ax.plot(weather['timestamp'], solar_elev, color='#E67E22', linewidth=0.8, alpha=0.7)

    # Horizon line
    ax.axhline(y=0, color='#E74C3C', linestyle='--', linewidth=1.5, alpha=0.7, label='Horizon')

    ax.set_xlabel('Date')
    ax.set_ylabel('Solar Elevation (°)')
    ax.set_title('Solar Elevation Throughout the Year')
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(frameon=False, loc='upper right')

    # Add y-axis padding and info
    elev_max = solar_elev.max()
    elev_min = solar_elev.min()
    elev_range = elev_max - elev_min
    ax.set_ylim(elev_min - elev_range * 0.1, elev_max + elev_range * 0.15)

    # Add statistics
    ax.text(0.02, 0.98, f'Max Elevation: {elev_max:.1f}°\nMin Elevation: {elev_min:.1f}°',
            transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    plt.tight_layout()
    return fig


def plot_temp_heatmap(weather):
    # Prepare data for heatmap
    weather_copy = weather.copy()
    weather_copy['hour'] = weather_copy['timestamp'].dt.hour
    weather_copy['month'] = weather_copy['timestamp'].dt.month

    pivot_data = weather_copy.pivot_table(
        values='T_out_C',
        index='hour',
        columns='month',
        aggfunc='mean'
    )

    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(pivot_data.values, cmap='RdYlBu_r', aspect='auto')

    # Set ticks
    ax.set_xticks(range(len(pivot_data.columns)))
    ax.set_xticklabels(pivot_data.columns)
    ax.set_yticks(range(0, 24, 2))
    ax.set_yticklabels(range(0, 24, 2))

    ax.set_xlabel('Month')
    ax.set_ylabel('Hour of Day')
    ax.set_title('Average Hourly Temperature by Month')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Temperature (°C)')

    # Add text annotations
    for i in range(len(pivot_data.index)):
        for j in range(len(pivot_data.columns)):
            val = pivot_data.values[i, j]
            if not np.isnan(val):
                text = ax.text(j, i, f'{val:.1f}',
                              ha="center", va="center", color="black", fontsize=8)

    plt.tight_layout()
    return fig


def plot_hourly_stacked_bar(results, solar_elev_max_year=None, weather=None, planes=None):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    hours = results['timestamp'].dt.hour
    width = 0.8
    t_out = results['T_out_C'].values

    # Heat OUT (losses) - shown as positive values
    trans = abs(results['Q_trans_h_W'].values / 1000)
    air = abs(results['Q_air_h_W'].values / 1000)

    ax1.bar(hours, trans, width, color='#1A5490', alpha=0.8, label='Transmission')
    ax1.bar(hours, air, width, bottom=trans, color='#5DADE2', alpha=0.8, label='Ventilation')

    ax1.set_xlabel('Hour of Day')
    ax1.set_ylabel('Power (kW)')
    ax1.set_title('Heat OUT')
    ax1.set_xticks(range(0, 24, 2))
    ax1.legend(frameon=False, loc='upper left')
    ax1.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.5)
    ax1.spines['top'].set_visible(False)

    # Set y-axis limits with padding
    max_out = (trans + air).max()
    ax1.set_ylim(0, max_out * 1.30)

    # Add temperature line on secondary axis
    ax1_temp = ax1.twinx()
    ax1_temp.plot(hours, t_out, color='#2C3E50', linewidth=2, marker='o', markersize=4, label='Outdoor Temp')

    # Add heating setpoint line
    from config import T_HEAT
    ax1_temp.axhline(y=T_HEAT, color='black', linestyle='--', linewidth=1, alpha=0.6, label=f'Heating Setpoint ({T_HEAT}°C)')

    # Add solar elevation to temperature legend
    temp_handles, temp_labels = ax1_temp.get_legend_handles_labels()
    if 'theta_s_deg' in results.columns:
        # Get solar elevation handle
        solar_elev_line = plt.Line2D([0], [0], color='#F39C12', linewidth=2, linestyle='--', label='Solar Elev')
        temp_handles.append(solar_elev_line)
        temp_labels.append('Solar Elev')

    ax1_temp.set_ylabel('Temperature (°C)')
    ax1_temp.spines['top'].set_visible(False)
    ax1_temp.legend(temp_handles, temp_labels, frameon=False, loc='upper right')

    # Set temperature y-axis limits with padding
    temp_min, temp_max = t_out.min(), t_out.max()
    temp_range = temp_max - temp_min
    ax1_temp.set_ylim(temp_min - temp_range * 0.15, temp_max + temp_range * 0.5)

    # Add solar elevation on third y-axis
    if 'theta_s_deg' in results.columns:
        ax1_solar = ax1.twinx()
        ax1_solar.spines['right'].set_position(('outward', 60))
        solar_elev = 90 - results['theta_s_deg'].values
        ax1_solar.plot(hours, solar_elev, color='#F39C12', linewidth=2, linestyle='--', alpha=1, label='Solar Elev')
        ax1_solar.set_ylabel('Solar Elevation (°)', color='#F39C12')
        ax1_solar.tick_params(axis='y', labelcolor='#F39C12')
        ax1_solar.spines['top'].set_visible(False)
        elev_max = solar_elev_max_year if solar_elev_max_year is not None else solar_elev.max()
        ax1_solar.set_ylim(0, elev_max * 1.2)

    # Heat IN (gains + HVAC) - shown as positive values, Solar on top
    solar = results['Q_solar_W'].values / 1000
    hvac = results['Q_heat_W'].values / 1000

    ax2.bar(hours, hvac, width, color='#E74C3C', alpha=0.9, label='HVAC')
    ax2.bar(hours, solar, width, bottom=hvac, color='#F39C12', alpha=0.8, label='Solar')

    # Add horizontal line for peak HVAC
    peak_hvac = hvac.max()
    ax2.axhline(y=peak_hvac, color='#E74C3C', linestyle='--', linewidth=1.2, alpha=0.6, label=f'Peak HVAC: {peak_hvac:.1f} kW')

    ax2.set_xlabel('Hour of Day')
    ax2.set_ylabel('Power (kW)')
    ax2.set_title('Heat IN')
    ax2.set_xticks(range(0, 24, 2))

    # Combine all legends
    handles, labels = ax2.get_legend_handles_labels()
    ax2.legend(handles, labels, frameon=False, loc='upper left')

    ax2.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.5)
    ax2.spines['top'].set_visible(False)

    # Set y-axis limits with padding
    max_in = (solar + hvac).max()
    ax2.set_ylim(0, max_in * 1.30)

    # Add temperature line on secondary axis
    ax2_temp = ax2.twinx()
    ax2_temp.plot(hours, t_out, color='#2C3E50', linewidth=2, marker='o', markersize=4, label='Outdoor Temp')
    ax2_temp.set_ylabel('Temperature (°C)')
    ax2_temp.spines['top'].set_visible(False)
    ax2_temp.legend(frameon=False, loc='upper right')

    # Set temperature y-axis limits with padding
    ax2_temp.set_ylim(temp_min - temp_range * 0.15, temp_max + temp_range * 0.5)

    # Add solar elevation on third y-axis
    if 'theta_s_deg' in results.columns:
        ax2_solar = ax2.twinx()
        ax2_solar.spines['right'].set_position(('outward', 60))
        solar_elev = 90 - results['theta_s_deg'].values
        ax2_solar.plot(hours, solar_elev, color='#F39C12', linewidth=2, linestyle='--', alpha=1, label='Solar Elev')
        ax2_solar.set_ylabel('Solar Elevation (°)', color='#F39C12')
        ax2_solar.tick_params(axis='y', labelcolor='#F39C12')
        ax2_solar.spines['top'].set_visible(False)
        elev_max_use = solar_elev_max_year if solar_elev_max_year is not None else solar_elev.max()
        ax2_solar.set_ylim(0, elev_max_use * 1.2)

    # Add IR radiation average as text
    if 'I_LW_Wm2' in results.columns:
        ir_avg = results['I_LW_Wm2'].mean()
        ax2.text(0.98, 0.03, f'IR Avg: {ir_avg:.0f} W/m²',
                transform=ax2.transAxes, fontsize=9,
                verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lavender', alpha=0.7))

    plt.tight_layout()
    return fig


def plot_heat_distribution(results):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))

    # Pie chart 1 - Heat OUT (losses)
    total_trans = abs(results['Q_trans_h_W'].sum()) / 1000
    total_air = abs(results['Q_air_h_W'].sum()) / 1000

    losses = [total_trans, total_air]
    loss_labels = [f'Transmission\n{total_trans:.1f} kWh', f'Ventilation\n{total_air:.1f} kWh']
    loss_colors = ['#1A5490', '#5DADE2']

    wedges, texts, autotexts = ax1.pie(losses, labels=loss_labels, colors=loss_colors,
                                        autopct='%1.1f%%', startangle=90)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
        autotext.set_weight('bold')

    total_loss = total_trans + total_air
    ax1.set_title(f'Heat OUT\nTotal: {total_loss:.1f} kWh')

    # Pie chart 2 - Heat IN (gains + HVAC)
    total_solar = abs(results['Q_solar_W'].sum()) / 1000
    total_hvac = abs(results['Q_heat_W'].sum()) / 1000
    total_int = abs(results['Q_int_W'].sum()) / 1000

    gains = []
    gain_labels = []
    gain_colors = []

    if total_solar > 0:
        gains.append(total_solar)
        gain_labels.append(f'Solar\n{total_solar:.1f} kWh')
        gain_colors.append('#F39C12')
    if total_hvac > 0:
        gains.append(total_hvac)
        gain_labels.append(f'HVAC\n{total_hvac:.1f} kWh')
        gain_colors.append('#E74C3C')
    if total_int > 0:
        gains.append(total_int)
        gain_labels.append(f'Internal\n{total_int:.1f} kWh')
        gain_colors.append('#9B59B6')

    wedges, texts, autotexts = ax2.pie(gains, labels=gain_labels, colors=gain_colors,
                                        autopct='%1.1f%%', startangle=90)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
        autotext.set_weight('bold')

    total_gain = sum(gains)
    ax2.set_title(f'Heat IN\nTotal: {total_gain:.1f} kWh')

    plt.tight_layout()
    return fig


def plot_hourly_stacked_bar_cooling(results, solar_elev_max_year=None, weather=None, planes=None):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    hours = results['timestamp'].dt.hour
    width = 0.8
    t_out = results['T_out_C'].values

    # Heat IN (gains) - shown as positive values
    trans = results['Q_trans_c_W'].values / 1000
    air = results['Q_air_c_W'].values / 1000
    solar = results['Q_solar_W'].values / 1000
    internal = results['Q_int_W'].values / 1000 if 'Q_int_W' in results.columns else np.zeros_like(trans)

    ax1.bar(hours, trans, width, color='#E74C3C', alpha=0.8, label='Transmission')
    ax1.bar(hours, air, width, bottom=trans, color='#27AE60', alpha=0.8, label='Ventilation')
    ax1.bar(hours, solar, width, bottom=trans+air, color='#F39C12', alpha=0.8, label='Solar')
    if internal.sum() > 0:
        ax1.bar(hours, internal, width, bottom=trans+air+solar, color='#9B59B6', alpha=0.8, label='Internal')

    ax1.set_xlabel('Hour of Day')
    ax1.set_ylabel('Power (kW)')
    ax1.set_title('Heat IN (Gains)')
    ax1.set_xticks(range(0, 24, 2))
    ax1.legend(frameon=False, loc='upper left')
    ax1.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.5)
    ax1.spines['top'].set_visible(False)

    # Set y-axis limits with padding
    max_in = (trans + air + solar + internal).max()
    ax1.set_ylim(0, max_in * 1.30)

    # Add temperature line on secondary axis
    ax1_temp = ax1.twinx()
    ax1_temp.plot(hours, t_out, color='#2C3E50', linewidth=2, marker='o', markersize=4, label='Outdoor Temp')

    # Add cooling setpoint line
    from config import T_COOL
    ax1_temp.axhline(y=T_COOL, color='black', linestyle='--', linewidth=1, alpha=0.6, label=f'Cooling Setpoint ({T_COOL}°C)')

    # Add solar elevation to temperature legend
    temp_handles, temp_labels = ax1_temp.get_legend_handles_labels()
    if 'theta_s_deg' in results.columns:
        # Get solar elevation handle
        solar_elev_line = plt.Line2D([0], [0], color='#F39C12', linewidth=2, linestyle='--', label='Solar Elev')
        temp_handles.append(solar_elev_line)
        temp_labels.append('Solar Elev')

    ax1_temp.set_ylabel('Temperature (°C)')
    ax1_temp.spines['top'].set_visible(False)
    ax1_temp.legend(temp_handles, temp_labels, frameon=False, loc='upper right')

    # Set temperature y-axis limits with padding
    temp_min, temp_max = t_out.min(), t_out.max()
    temp_range = temp_max - temp_min
    ax1_temp.set_ylim(temp_min - temp_range * 0.15, temp_max + temp_range * 0.5)

    # Add solar elevation on third y-axis
    if 'theta_s_deg' in results.columns:
        ax1_solar = ax1.twinx()
        ax1_solar.spines['right'].set_position(('outward', 60))
        solar_elev = 90 - results['theta_s_deg'].values
        ax1_solar.plot(hours, solar_elev, color='#F39C12', linewidth=2, linestyle='--', alpha=1, label='Solar Elev')
        ax1_solar.set_ylabel('Solar Elevation (°)', color='#F39C12')
        ax1_solar.tick_params(axis='y', labelcolor='#F39C12')
        ax1_solar.spines['top'].set_visible(False)
        elev_max = solar_elev_max_year if solar_elev_max_year is not None else solar_elev.max()
        ax1_solar.set_ylim(0, elev_max * 1.2)

    # Heat OUT (cooling) - shown as positive values
    cooling = results['Q_cool_W'].values / 1000

    ax2.bar(hours, cooling, width, color='#1A5490', alpha=0.9, label='Cooling')

    # Add horizontal line for peak cooling
    peak_cool = cooling.max()
    ax2.axhline(y=peak_cool, color='#1A5490', linestyle='--', linewidth=1.2, alpha=0.6, label=f'Peak Cooling: {peak_cool:.1f} kW')

    ax2.set_xlabel('Hour of Day')
    ax2.set_ylabel('Power (kW)')
    ax2.set_title('Heat OUT (Cooling)')
    ax2.set_xticks(range(0, 24, 2))

    # Combine all legends
    handles, labels = ax2.get_legend_handles_labels()
    ax2.legend(handles, labels, frameon=False, loc='upper left')

    ax2.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.5)
    ax2.spines['top'].set_visible(False)

    # Set y-axis limits with padding
    max_out = cooling.max()
    ax2.set_ylim(0, max_out * 1.30)

    # Add temperature line on secondary axis
    ax2_temp = ax2.twinx()
    ax2_temp.plot(hours, t_out, color='#2C3E50', linewidth=2, marker='o', markersize=4, label='Outdoor Temp')
    ax2_temp.set_ylabel('Temperature (°C)')
    ax2_temp.spines['top'].set_visible(False)
    ax2_temp.legend(frameon=False, loc='upper right')

    # Set temperature y-axis limits with padding
    ax2_temp.set_ylim(temp_min - temp_range * 0.15, temp_max + temp_range * 0.5)

    # Add solar elevation on third y-axis
    if 'theta_s_deg' in results.columns:
        ax2_solar = ax2.twinx()
        ax2_solar.spines['right'].set_position(('outward', 60))
        solar_elev = 90 - results['theta_s_deg'].values
        ax2_solar.plot(hours, solar_elev, color='#F39C12', linewidth=2, linestyle='--', alpha=1, label='Solar Elev')
        ax2_solar.set_ylabel('Solar Elevation (°)', color='#F39C12')
        ax2_solar.tick_params(axis='y', labelcolor='#F39C12')
        ax2_solar.spines['top'].set_visible(False)
        elev_max_use = solar_elev_max_year if solar_elev_max_year is not None else solar_elev.max()
        ax2_solar.set_ylim(0, elev_max_use * 1.2)

    # Add IR radiation average as text
    if 'I_LW_Wm2' in results.columns:
        ir_avg = results['I_LW_Wm2'].mean()
        ax2.text(0.98, 0.03, f'IR Avg: {ir_avg:.0f} W/m²',
                transform=ax2.transAxes, fontsize=9,
                verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lavender', alpha=0.7))

    plt.tight_layout()
    return fig


def plot_heat_distribution_detailed(results, air, gains, T_heat, T_cool):
    """Detailed 2-pie chart with ventilation/infiltration and internal gains breakdown"""
    from config import RHO_AIR, CP_AIR

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # Calculate detailed components
    heating_mask = results['Q_heat_W'] > 0
    cooling_mask = results['Q_cool_W'] > 0

    # Ventilation and infiltration components
    V_inf_m3s = air.ACH_infiltration_h * air.V_zone_m3 / 3600.0

    # === PIE 1: HEATING - HEAT OUT (detailed losses) ===
    if heating_mask.any():
        # Transmission (same as before)
        total_trans_h = abs(results.loc[heating_mask, 'Q_trans_h_W'].sum()) / 1000

        # Split ventilation into ventilation + infiltration
        dT_h = results.loc[heating_mask, 'T_out_C'].values - T_heat
        Q_vent_h = RHO_AIR * CP_AIR * air.Vdot_vent_m3s * (1.0 - air.eta_HRV) * dT_h
        Q_inf_h = RHO_AIR * CP_AIR * V_inf_m3s * dT_h
        total_vent_h = abs(Q_vent_h.sum()) / 1000
        total_inf_h = abs(Q_inf_h.sum()) / 1000

        losses = [total_trans_h, total_vent_h, total_inf_h]
        loss_labels = [
            f'Transmission ({total_trans_h:.1f} kWh)',
            f'Ventilation ({total_vent_h:.1f} kWh)',
            f'Infiltration ({total_inf_h:.1f} kWh)'
        ]
        loss_colors = ['#1A5490', '#5DADE2', '#85C1E9']

        wedges, texts, autotexts = axes[0].pie(losses, colors=loss_colors,
                                            autopct='%1.1f%%', startangle=45)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_weight('bold')

        axes[0].legend(wedges, loss_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)

        total_loss = sum(losses)
        axes[0].set_title(f'DETAILED - HEATING\nHeat OUT (Losses)\nTotal: {total_loss:.1f} kWh',
                         fontsize=13, fontweight='bold', pad=20)
    else:
        axes[0].text(0.5, 0.5, 'No Heating\nRequired', ha='center', va='center', fontsize=14)
        axes[0].set_title('DETAILED - HEATING\nHeat OUT (Losses)', fontsize=13, fontweight='bold', pad=20)

    # === PIE 2: COOLING - HEAT IN (detailed gains) ===
    if cooling_mask.any():
        # Transmission and ventilation (clipped to positive only)
        total_trans_c = np.maximum(0, results.loc[cooling_mask, 'Q_trans_c_W'].values).sum() / 1000

        # Split ventilation into ventilation + infiltration
        dT_c = results.loc[cooling_mask, 'T_out_C'].values - T_cool
        Q_vent_c = RHO_AIR * CP_AIR * air.Vdot_vent_m3s * (1.0 - air.eta_HRV) * dT_c
        Q_inf_c = RHO_AIR * CP_AIR * V_inf_m3s * dT_c
        total_vent_c = np.maximum(0, Q_vent_c).sum() / 1000
        total_inf_c = np.maximum(0, Q_inf_c).sum() / 1000

        # Solar
        total_solar_c = results.loc[cooling_mask, 'Q_solar_W'].sum() / 1000

        # Split internal gains into components
        if gains is not None:
            n_cool = cooling_mask.sum()
            total_equip_c = gains.Q_equip_kW * n_cool
            total_occ_c = gains.Q_occ_kW * n_cool
            total_light_c = gains.Q_light_kW * n_cool
        else:
            total_equip_c = 0.0
            total_occ_c = 0.0
            total_light_c = 0.0

        gains_c = []
        gain_labels_c = []
        gain_colors_c = []

        # Add all non-zero components
        if total_trans_c > 0.1:
            gains_c.append(total_trans_c)
            gain_labels_c.append(f'Transmission ({total_trans_c:.1f} kWh)')
            gain_colors_c.append('#E74C3C')
        if total_vent_c > 0.1:
            gains_c.append(total_vent_c)
            gain_labels_c.append(f'Ventilation ({total_vent_c:.1f} kWh)')
            gain_colors_c.append('#27AE60')
        if total_inf_c > 0.1:
            gains_c.append(total_inf_c)
            gain_labels_c.append(f'Infiltration ({total_inf_c:.1f} kWh)')
            gain_colors_c.append('#52BE80')
        if total_solar_c > 0.1:
            gains_c.append(total_solar_c)
            gain_labels_c.append(f'Solar ({total_solar_c:.1f} kWh)')
            gain_colors_c.append('#F39C12')
        if total_equip_c > 0.1:
            gains_c.append(total_equip_c)
            gain_labels_c.append(f'Equipment ({total_equip_c:.1f} kWh)')
            gain_colors_c.append('#9B59B6')
        if total_occ_c > 0.1:
            gains_c.append(total_occ_c)
            gain_labels_c.append(f'Occupancy ({total_occ_c:.1f} kWh)')
            gain_colors_c.append('#8E44AD')
        if total_light_c > 0.1:
            gains_c.append(total_light_c)
            gain_labels_c.append(f'Lighting ({total_light_c:.1f} kWh)')
            gain_colors_c.append('#D68910')

        wedges, texts, autotexts = axes[1].pie(gains_c, colors=gain_colors_c,
                                            autopct='%1.1f%%', startangle=140)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_weight('bold')

        axes[1].legend(wedges, gain_labels_c, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)

        total_gain_c = sum(gains_c)
        axes[1].set_title(f'DETAILED - COOLING\nHeat IN (Gains)\nTotal: {total_gain_c:.1f} kWh',
                         fontsize=13, fontweight='bold', pad=20)
    else:
        axes[1].text(0.5, 0.5, 'No Cooling\nRequired', ha='center', va='center', fontsize=14)
        axes[1].set_title('DETAILED - COOLING\nHeat IN (Gains)', fontsize=13, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.5)
    return fig


def plot_heat_distribution_4pies(results):
    """2-pie chart: coldest day heating heat OUT and cooling heat IN"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # Filter hours when heating is active (Q_heat > 0)
    heating_mask = results['Q_heat_W'] > 0
    # Filter hours when cooling is active (Q_cool > 0)
    cooling_mask = results['Q_cool_W'] > 0

    # === PIE 1: HEATING - HEAT OUT (losses) ===
    if heating_mask.any():
        total_trans_h = abs(results.loc[heating_mask, 'Q_trans_h_W'].sum()) / 1000
        total_air_h = abs(results.loc[heating_mask, 'Q_air_h_W'].sum()) / 1000

        losses = [total_trans_h, total_air_h]
        loss_labels = [f'Transmission ({total_trans_h:.1f} kWh)', f'Ventilation ({total_air_h:.1f} kWh)']
        loss_colors = ['#1A5490', '#5DADE2']

        wedges, texts, autotexts = axes[0].pie(losses, colors=loss_colors,
                                            autopct='%1.1f%%', startangle=45)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_weight('bold')

        axes[0].legend(wedges, loss_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=11)

        total_loss = total_trans_h + total_air_h
        axes[0].set_title(f'COLDEST DAY - HEATING\nHeat OUT (Losses)\nTotal: {total_loss:.1f} kWh',
                         fontsize=13, fontweight='bold', pad=20)
    else:
        axes[0].text(0.5, 0.5, 'No Heating\nRequired', ha='center', va='center', fontsize=14)
        axes[0].set_title('COLDEST DAY - HEATING\nHeat OUT (Losses)', fontsize=13, fontweight='bold', pad=20)

    # === PIE 2: COOLING - HEAT IN (gains) ===
    if cooling_mask.any():
        # Clip to 0 if negative (free cooling = helping HVAC, so exclude per design principle)
        total_trans_c = np.maximum(0, results.loc[cooling_mask, 'Q_trans_c_W'].values).sum() / 1000
        total_air_c = np.maximum(0, results.loc[cooling_mask, 'Q_air_c_W'].values).sum() / 1000
        total_solar_c = results.loc[cooling_mask, 'Q_solar_W'].sum() / 1000
        total_int_c = results.loc[cooling_mask, 'Q_int_W'].sum() / 1000 if 'Q_int_W' in results.columns else 0.0

        gains_c = []
        gain_labels_c = []
        gain_colors_c = []

        # Show only positive heat gains (conservative design)
        if total_trans_c > 0.1:
            gains_c.append(total_trans_c)
            gain_labels_c.append(f'Transmission ({total_trans_c:.1f} kWh)')
            gain_colors_c.append('#E74C3C')
        if total_air_c > 0.1:
            gains_c.append(total_air_c)
            gain_labels_c.append(f'Ventilation ({total_air_c:.1f} kWh)')
            gain_colors_c.append('#27AE60')
        if total_solar_c > 0:
            gains_c.append(total_solar_c)
            gain_labels_c.append(f'Solar ({total_solar_c:.1f} kWh)')
            gain_colors_c.append('#F39C12')
        if total_int_c > 0:
            gains_c.append(total_int_c)
            gain_labels_c.append(f'Internal ({total_int_c:.1f} kWh)')
            gain_colors_c.append('#9B59B6')

        wedges, texts, autotexts = axes[1].pie(gains_c, colors=gain_colors_c,
                                            autopct='%1.1f%%', startangle=140)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_weight('bold')

        axes[1].legend(wedges, gain_labels_c, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=11)

        total_gain_c = sum(gains_c)
        axes[1].set_title(f'COLDEST DAY - COOLING\nHeat IN (Gains)\nTotal: {total_gain_c:.1f} kWh',
                         fontsize=13, fontweight='bold', pad=20)
    else:
        axes[1].text(0.5, 0.5, 'No Cooling\nRequired', ha='center', va='center', fontsize=14)
        axes[1].set_title('COLDEST DAY - COOLING\nHeat IN (Gains)', fontsize=13, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.5)
    return fig


def plot_design_days(heat_weather, cool_weather):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # Heating day temperature
    axes[0, 0].plot(heat_weather['timestamp'].dt.hour, heat_weather['T_out_C'],
                    marker='o', color='#3498DB', linewidth=2, markersize=6)
    axes[0, 0].set_xlabel('Hour')
    axes[0, 0].set_ylabel('Temperature (°C)')
    axes[0, 0].set_title('Heating Design Day - Temperature')
    axes[0, 0].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[0, 0].spines['top'].set_visible(False)
    axes[0, 0].spines['right'].set_visible(False)
    axes[0, 0].set_xticks(range(0, 24, 3))

    # Cooling day temperature
    axes[0, 1].plot(cool_weather['timestamp'].dt.hour, cool_weather['T_out_C'],
                    marker='o', color='#E74C3C', linewidth=2, markersize=6)
    axes[0, 1].set_xlabel('Hour')
    axes[0, 1].set_ylabel('Temperature (°C)')
    axes[0, 1].set_title('Cooling Design Day - Temperature')
    axes[0, 1].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[0, 1].spines['top'].set_visible(False)
    axes[0, 1].spines['right'].set_visible(False)
    axes[0, 1].set_xticks(range(0, 24, 3))

    # Heating day solar
    axes[1, 0].plot(heat_weather['timestamp'].dt.hour, heat_weather['I_dir_Wm2'],
                    marker='o', color='#E67E22', linewidth=2, markersize=6, label='Direct')
    axes[1, 0].plot(heat_weather['timestamp'].dt.hour, heat_weather['I_dif_Wm2'],
                    marker='s', color='#95A5A6', linewidth=2, markersize=6, label='Diffuse')
    axes[1, 0].set_xlabel('Hour')
    axes[1, 0].set_ylabel('Irradiance (W/m²)')
    axes[1, 0].set_title('Heating Design Day - Solar Radiation')
    axes[1, 0].legend(frameon=False)
    axes[1, 0].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[1, 0].spines['top'].set_visible(False)
    axes[1, 0].spines['right'].set_visible(False)
    axes[1, 0].set_xticks(range(0, 24, 3))

    # Cooling day solar
    axes[1, 1].plot(cool_weather['timestamp'].dt.hour, cool_weather['I_dir_Wm2'],
                    marker='o', color='#E67E22', linewidth=2, markersize=6, label='Direct')
    axes[1, 1].plot(cool_weather['timestamp'].dt.hour, cool_weather['I_dif_Wm2'],
                    marker='s', color='#95A5A6', linewidth=2, markersize=6, label='Diffuse')
    axes[1, 1].set_xlabel('Hour')
    axes[1, 1].set_ylabel('Irradiance (W/m²)')
    axes[1, 1].set_title('Cooling Design Day - Solar Radiation')
    axes[1, 1].legend(frameon=False)
    axes[1, 1].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[1, 1].spines['top'].set_visible(False)
    axes[1, 1].spines['right'].set_visible(False)
    axes[1, 1].set_xticks(range(0, 24, 3))

    plt.tight_layout()
    return fig
