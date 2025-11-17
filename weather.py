import pandas as pd
import numpy as np


def load_epw_weather(epw_path):
    epw_cols = [
        'Year', 'Month', 'Day', 'Hour', 'Minute',
        'Data_Source', 'Dry_Bulb_Temperature', 'Dew_Point_Temperature',
        'Relative_Humidity', 'Atmospheric_Station_Pressure', 'Extraterrestrial_Horizontal_Radiation',
        'Extraterrestrial_Direct_Normal_Radiation', 'Horizontal_Infrared_Radiation_Intensity',
        'Global_Horizontal_Radiation', 'Direct_Normal_Radiation', 'Diffuse_Horizontal_Radiation',
        'Global_Horizontal_Illuminance', 'Direct_Normal_Illuminance', 'Diffuse_Horizontal_Illuminance',
        'Zenith_Luminance', 'Wind_Direction', 'Wind_Speed', 'Total_Sky_Cover',
        'Opaque_Sky_Cover', 'Visibility', 'Ceiling_Height', 'Present_Weather_Observation',
        'Present_Weather_Codes', 'Precipitable_Water', 'Aerosol_Optical_Depth',
        'Snow_Depth', 'Days_Since_Last_Snowfall', 'Albedo', 'Liquid_Precipitation_Depth',
        'Liquid_Precipitation_Quantity'
    ]

    with open(epw_path, 'r', encoding='latin-1') as f:
        header = [f.readline().strip() for _ in range(8)]

    loc = header[0].split(',')
    lat = float(loc[6])

    # Get ground temps at 2m depth from header
    gnd_line = header[3].split(',')
    gnd_temps = [float(gnd_line[i]) for i in range(23, 35)]

    weather = pd.read_csv(epw_path, skiprows=8, header=None, names=epw_cols, encoding='latin-1')

    weather['DateTime'] = pd.to_datetime({
        'year': weather['Year'],
        'month': weather['Month'],
        'day': weather['Day'],
        'hour': weather['Hour'] - 1
    })

    # Solar position calc
    def solar_pos(lat, doy, hr):
        decl = 23.45 * np.sin(np.radians(360 * (284 + doy) / 365))
        ha = 15 * (hr - 12)
        lat_r = np.radians(lat)
        dec_r = np.radians(decl)
        ha_r = np.radians(ha)

        elev = np.degrees(np.arcsin(np.sin(lat_r) * np.sin(dec_r) + np.cos(lat_r) * np.cos(dec_r) * np.cos(ha_r)))
        azim = np.degrees(np.arctan2(np.sin(ha_r), np.cos(ha_r) * np.sin(lat_r) - np.tan(dec_r) * np.cos(lat_r)))

        return 90.0 - elev, azim

    weather['Day_of_Year'] = weather['DateTime'].dt.dayofyear
    angles = [solar_pos(lat, d, h) for d, h in zip(weather['Day_of_Year'], weather['Hour'])]
    weather['theta_s_deg'], weather['phi_s_deg'] = zip(*angles)
    weather['T_ground_C'] = weather['Month'].map(lambda m: gnd_temps[m - 1])

    return pd.DataFrame({
        'timestamp': weather['DateTime'],
        'T_out_C': weather['Dry_Bulb_Temperature'],
        'I_dir_Wm2': weather['Direct_Normal_Radiation'],
        'I_dif_Wm2': weather['Diffuse_Horizontal_Radiation'],
        'theta_s_deg': weather['theta_s_deg'],
        'phi_s_deg': weather['phi_s_deg'],
        'I_LW_Wm2': weather['Horizontal_Infrared_Radiation_Intensity'],
        'T_ground_C': weather['T_ground_C']
    })
