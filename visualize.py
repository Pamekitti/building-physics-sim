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

    # Diffuse radiation over year
    axes[0, 1].plot(weather['timestamp'], weather['I_dif_Wm2'],
                    color='#95A5A6', linewidth=0.8, alpha=0.7)
    axes[0, 1].set_ylabel('Irradiance (W/m²)')
    axes[0, 1].set_title('Diffuse Horizontal Radiation')
    axes[0, 1].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[0, 1].spines['top'].set_visible(False)
    axes[0, 1].spines['right'].set_visible(False)

    # Infrared radiation over year
    axes[1, 0].plot(weather['timestamp'], weather['I_LW_Wm2'],
                    color='#8E44AD', linewidth=0.8, alpha=0.7)
    axes[1, 0].set_ylabel('Irradiance (W/m²)')
    axes[1, 0].set_title('Longwave Infrared Radiation')
    axes[1, 0].grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    axes[1, 0].spines['top'].set_visible(False)
    axes[1, 0].spines['right'].set_visible(False)

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
    ax.axhline(y=0, color='#E74C3C', linestyle='--', linewidth=1.5, alpha=0.7)

    ax.set_xlabel('Date')
    ax.set_ylabel('Solar Elevation (°)')
    ax.set_title('Solar Elevation Throughout the Year')
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

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
