import matplotlib.pyplot as plt
import numpy as np


def plot_temp_overview(weather):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # Outdoor temp over year
    axes[0, 0].plot(weather['timestamp'], weather['T_out_C'],
                    color='#2C3E50', linewidth=0.8, alpha=0.8)
    axes[0, 0].set_ylabel('Temperature (°C)')
    axes[0, 0].set_title('Outdoor Temperature - Typical Year')
    axes[0, 0].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[0, 0].spines['top'].set_visible(False)
    axes[0, 0].spines['right'].set_visible(False)

    # Add y-axis padding
    temp_min = weather['T_out_C'].min()
    temp_max = weather['T_out_C'].max()
    temp_range = temp_max - temp_min
    axes[0, 0].set_ylim(temp_min - temp_range * 0.1, temp_max + temp_range * 0.1)

    # Temp distribution
    axes[0, 1].hist(weather['T_out_C'], bins=40, color='#34495E',
                    edgecolor='white', linewidth=0.5)
    axes[0, 1].set_xlabel('Temperature (°C)')
    axes[0, 1].set_ylabel('Frequency (hours)')
    axes[0, 1].set_title('Temperature Distribution')
    axes[0, 1].grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.5)
    axes[0, 1].spines['top'].set_visible(False)
    axes[0, 1].spines['right'].set_visible(False)

    # Ground vs outdoor temp comparison
    monthly_out = weather.groupby(weather['timestamp'].dt.month)['T_out_C'].mean()
    monthly_gnd = weather.groupby(weather['timestamp'].dt.month)['T_ground_C'].mean()
    axes[1, 0].plot(monthly_out.index, monthly_out.values, marker='o', color='#2C3E50',
                    linewidth=2, markersize=6, label='Outdoor')
    axes[1, 0].plot(monthly_gnd.index, monthly_gnd.values, marker='s', color='#7F8C8D',
                    linewidth=2, markersize=6, label='Ground (2m)')
    axes[1, 0].set_xlabel('Month')
    axes[1, 0].set_ylabel('Temperature (°C)')
    axes[1, 0].set_title('Monthly Average Temperatures')
    axes[1, 0].legend(frameon=False)
    axes[1, 0].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[1, 0].spines['top'].set_visible(False)
    axes[1, 0].spines['right'].set_visible(False)

    # Add y-axis padding
    monthly_min = min(monthly_out.min(), monthly_gnd.min())
    monthly_max = max(monthly_out.max(), monthly_gnd.max())
    monthly_range = monthly_max - monthly_min
    axes[1, 0].set_ylim(monthly_min - monthly_range * 0.1, monthly_max + monthly_range * 0.1)

    # Design conditions
    temps = weather['T_out_C']
    heat_design = np.percentile(temps, 0.4)
    cool_design = np.percentile(temps, 99.6)
    axes[1, 1].hist(temps, bins=40, color='#34495E', edgecolor='white', linewidth=0.5)
    axes[1, 1].axvline(heat_design, color='#3498DB', linestyle='--', linewidth=2,
                       label=f'Heating: {heat_design:.1f}°C')
    axes[1, 1].axvline(cool_design, color='#E74C3C', linestyle='--', linewidth=2,
                       label=f'Cooling: {cool_design:.1f}°C')
    axes[1, 1].set_xlabel('Temperature (°C)')
    axes[1, 1].set_ylabel('Frequency (hours)')
    axes[1, 1].set_title('Design Conditions')
    axes[1, 1].legend(frameon=False)
    axes[1, 1].grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.5)
    axes[1, 1].spines['top'].set_visible(False)
    axes[1, 1].spines['right'].set_visible(False)

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
    ax1_temp.plot(hours, t_out, color='#2C3E50', linewidth=2, marker='o', markersize=4, label='T_out')

    # Calculate and plot sol-air temperature if weather data provided
    if weather is not None and planes is not None:
        from physics import cos_incidence, plane_irradiance, sol_air_temp
        from config import H_E

        # Calculate T-sol for south wall (typical surface)
        south_wall = next((p for p in planes if 'WW-S' in p.name and p.is_opaque() and not p.ground_contact), None)
        if south_wall is not None:
            cos_i = cos_incidence(weather['theta_s_deg'].values, weather['phi_s_deg'].values,
                                south_wall.tilt_deg, south_wall.azimuth_deg)
            I_p = plane_irradiance(weather['I_dir_Wm2'].values, weather['I_dif_Wm2'].values,
                                 cos_i, south_wall.tilt_deg)
            I_LW = weather['I_LW_Wm2'].values if 'I_LW_Wm2' in weather.columns else None
            t_sol_wall = sol_air_temp(weather['T_out_C'].values, I_p, south_wall.alpha,
                                     south_wall.epsilon, I_LW, H_E)
            ax1_temp.plot(hours, t_sol_wall, color='#E67E22', linewidth=2, linestyle='--',
                         marker='s', markersize=3, alpha=0.8, label='T_sol (wall)')

        # Calculate T-sol for roof
        roof = next((p for p in planes if 'WW-RN' in p.name and p.is_opaque()), None)
        if roof is not None:
            cos_i = cos_incidence(weather['theta_s_deg'].values, weather['phi_s_deg'].values,
                                roof.tilt_deg, roof.azimuth_deg)
            I_p = plane_irradiance(weather['I_dir_Wm2'].values, weather['I_dif_Wm2'].values,
                                 cos_i, roof.tilt_deg)
            t_sol_roof = sol_air_temp(weather['T_out_C'].values, I_p, roof.alpha,
                                    roof.epsilon, I_LW, H_E)
            ax1_temp.plot(hours, t_sol_roof, color='#C0392B', linewidth=2, linestyle=':',
                         marker='^', markersize=3, alpha=0.8, label='T_sol (roof)')

    ax1_temp.set_ylabel('Temperature (°C)')
    ax1_temp.spines['top'].set_visible(False)
    ax1_temp.legend(frameon=False, loc='upper right')

    # Set temperature y-axis limits with padding (include T-sol in range)
    temp_min, temp_max = t_out.min(), t_out.max()
    if weather is not None and planes is not None:
        all_temps = [t_out]
        if south_wall is not None:
            all_temps.append(t_sol_wall)
        if roof is not None:
            all_temps.append(t_sol_roof)
        temp_min = min(np.min(t) for t in all_temps)
        temp_max = max(np.max(t) for t in all_temps)
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
    total_kitchen = abs(results['Q_kitchen_W'].sum()) / 1000

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
    if total_kitchen > 0:
        gains.append(total_kitchen)
        gain_labels.append(f'Kitchen\n{total_kitchen:.1f} kWh')
        gain_colors.append('#16A085')

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
    ax1_temp.plot(hours, t_out, color='#2C3E50', linewidth=2, marker='o', markersize=4, label='T_out')

    # Calculate and plot sol-air temperature if weather data provided
    if weather is not None and planes is not None:
        from physics import cos_incidence, plane_irradiance, sol_air_temp
        from config import H_E

        # Calculate T-sol for south wall
        south_wall = next((p for p in planes if 'WW-S' in p.name and p.is_opaque() and not p.ground_contact), None)
        if south_wall is not None:
            cos_i = cos_incidence(weather['theta_s_deg'].values, weather['phi_s_deg'].values,
                                south_wall.tilt_deg, south_wall.azimuth_deg)
            I_p = plane_irradiance(weather['I_dir_Wm2'].values, weather['I_dif_Wm2'].values,
                                 cos_i, south_wall.tilt_deg)
            I_LW = weather['I_LW_Wm2'].values if 'I_LW_Wm2' in weather.columns else None
            t_sol_wall = sol_air_temp(weather['T_out_C'].values, I_p, south_wall.alpha,
                                     south_wall.epsilon, I_LW, H_E)
            ax1_temp.plot(hours, t_sol_wall, color='#E67E22', linewidth=2, linestyle='--',
                         marker='s', markersize=3, alpha=0.8, label='T_sol (wall)')

        # Calculate T-sol for roof
        roof = next((p for p in planes if 'WW-RN' in p.name and p.is_opaque()), None)
        if roof is not None:
            cos_i = cos_incidence(weather['theta_s_deg'].values, weather['phi_s_deg'].values,
                                roof.tilt_deg, roof.azimuth_deg)
            I_p = plane_irradiance(weather['I_dir_Wm2'].values, weather['I_dif_Wm2'].values,
                                 cos_i, roof.tilt_deg)
            t_sol_roof = sol_air_temp(weather['T_out_C'].values, I_p, roof.alpha,
                                    roof.epsilon, I_LW, H_E)
            ax1_temp.plot(hours, t_sol_roof, color='#C0392B', linewidth=2, linestyle=':',
                         marker='^', markersize=3, alpha=0.8, label='T_sol (roof)')

    ax1_temp.set_ylabel('Temperature (°C)')
    ax1_temp.spines['top'].set_visible(False)
    ax1_temp.legend(frameon=False, loc='upper right')

    # Set temperature y-axis limits with padding (include T-sol)
    temp_min, temp_max = t_out.min(), t_out.max()
    if weather is not None and planes is not None:
        all_temps = [t_out]
        if south_wall is not None:
            all_temps.append(t_sol_wall)
        if roof is not None:
            all_temps.append(t_sol_roof)
        temp_min = min(np.min(t) for t in all_temps)
        temp_max = max(np.max(t) for t in all_temps)
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


def plot_heat_distribution_4pies(results):
    """4-pie chart showing both heating and cooling components"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Filter hours when heating is active (Q_heat > 0)
    heating_mask = results['Q_heat_W'] > 0
    # Filter hours when cooling is active (Q_cool > 0)
    cooling_mask = results['Q_cool_W'] > 0

    # === HEATING COMPONENTS ===
    # Pie 1 - Heat OUT (losses) during heating hours
    if heating_mask.any():
        total_trans_h = abs(results.loc[heating_mask, 'Q_trans_h_W'].sum()) / 1000
        total_air_h = abs(results.loc[heating_mask, 'Q_air_h_W'].sum()) / 1000

        losses = [total_trans_h, total_air_h]
        loss_labels = [f'Transmission ({total_trans_h:.1f} kWh)', f'Ventilation ({total_air_h:.1f} kWh)']
        loss_colors = ['#1A5490', '#5DADE2']

        wedges, texts, autotexts = axes[0, 0].pie(losses, colors=loss_colors,
                                            autopct='%1.1f%%', startangle=45)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_weight('bold')

        axes[0, 0].legend(wedges, loss_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)

        total_loss = total_trans_h + total_air_h
        axes[0, 0].set_title(f'HEATING - Heat OUT\nTotal: {total_loss:.1f} kWh')
    else:
        axes[0, 0].text(0.5, 0.5, 'No Heating\nRequired', ha='center', va='center', fontsize=14)
        axes[0, 0].set_title('HEATING - Heat OUT')

    # Pie 2 - Heat IN (HVAC only) during heating hours
    # Conservative design: solar and internal gains are excluded from heating calculations
    if heating_mask.any():
        total_hvac_h = results.loc[heating_mask, 'Q_heat_W'].sum() / 1000

        gains = []
        gain_labels = []
        gain_colors = []

        if total_hvac_h > 0:
            gains.append(total_hvac_h)
            gain_labels.append(f'HVAC ({total_hvac_h:.1f} kWh)')
            gain_colors.append('#E74C3C')

        wedges, texts, autotexts = axes[0, 1].pie(gains, colors=gain_colors,
                                            autopct='%1.1f%%', startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_weight('bold')

        axes[0, 1].legend(wedges, gain_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)

        total_gain = sum(gains)
        axes[0, 1].set_title(f'HEATING - Heat IN\nTotal: {total_gain:.1f} kWh')
    else:
        axes[0, 1].text(0.5, 0.5, 'No Heating\nRequired', ha='center', va='center', fontsize=14)
        axes[0, 1].set_title('HEATING - Heat IN')

    # === COOLING COMPONENTS ===
    # Pie 3 - Heat IN (gains) during cooling hours
    # Use actual values (not clipped) so totals match Heat OUT
    if cooling_mask.any():
        # Sum actual values during cooling hours (can be negative for free cooling)
        total_trans_c = results.loc[cooling_mask, 'Q_trans_c_W'].sum() / 1000
        total_air_c = results.loc[cooling_mask, 'Q_air_c_W'].sum() / 1000
        total_solar_c = results.loc[cooling_mask, 'Q_solar_W'].sum() / 1000
        total_int_c = results.loc[cooling_mask, 'Q_int_W'].sum() / 1000 if 'Q_int_W' in results.columns else 0.0
        total_kitchen_c = results.loc[cooling_mask, 'Q_kitchen_W'].sum() / 1000 if 'Q_kitchen_W' in results.columns else 0.0

        gains_c = []
        gain_labels_c = []
        gain_colors_c = []

        # Show all non-zero components (even if negative - represents free cooling offset)
        if abs(total_trans_c) > 0.1:
            gains_c.append(total_trans_c)
            sign = '+' if total_trans_c > 0 else ''
            gain_labels_c.append(f'Transmission ({sign}{total_trans_c:.1f} kWh)')
            gain_colors_c.append('#E74C3C' if total_trans_c > 0 else '#5DADE2')
        if abs(total_air_c) > 0.1:
            gains_c.append(total_air_c)
            sign = '+' if total_air_c > 0 else ''
            gain_labels_c.append(f'Ventilation ({sign}{total_air_c:.1f} kWh)')
            gain_colors_c.append('#27AE60' if total_air_c > 0 else '#95A5A6')
        if total_solar_c > 0:
            gains_c.append(total_solar_c)
            gain_labels_c.append(f'Solar ({total_solar_c:.1f} kWh)')
            gain_colors_c.append('#F39C12')
        if total_int_c > 0:
            gains_c.append(total_int_c)
            gain_labels_c.append(f'Internal ({total_int_c:.1f} kWh)')
            gain_colors_c.append('#9B59B6')
        if total_kitchen_c > 0:
            gains_c.append(total_kitchen_c)
            gain_labels_c.append(f'Kitchen ({total_kitchen_c:.1f} kWh)')
            gain_colors_c.append('#16A085')

        wedges, texts, autotexts = axes[1, 0].pie(gains_c, colors=gain_colors_c,
                                            autopct='%1.1f%%', startangle=140)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_weight('bold')

        axes[1, 0].legend(wedges, gain_labels_c, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)

        total_gain_c = sum(gains_c)
        axes[1, 0].set_title(f'COOLING - Heat IN\nTotal: {total_gain_c:.1f} kWh')
    else:
        axes[1, 0].text(0.5, 0.5, 'No Cooling\nRequired', ha='center', va='center', fontsize=14)
        axes[1, 0].set_title('COOLING - Heat IN')

    # Pie 4 - Heat OUT (cooling) during cooling hours
    if cooling_mask.any():
        total_cool = results.loc[cooling_mask, 'Q_cool_W'].sum() / 1000

        cooling_parts = [total_cool]
        cooling_labels = [f'Cooling ({total_cool:.1f} kWh)']
        cooling_colors = ['#1A5490']

        wedges, texts, autotexts = axes[1, 1].pie(cooling_parts, colors=cooling_colors,
                                            autopct='%1.1f%%', startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_weight('bold')

        axes[1, 1].legend(wedges, cooling_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)

        axes[1, 1].set_title(f'COOLING - Heat OUT\nTotal: {total_cool:.1f} kWh')
    else:
        axes[1, 1].text(0.5, 0.5, 'No Cooling\nRequired', ha='center', va='center', fontsize=14)
        axes[1, 1].set_title('COOLING - Heat OUT')

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.4, hspace=0.3)
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
