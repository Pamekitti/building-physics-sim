# Building Heating & Cooling Load Calculator

A Python tool for calculating design heating and cooling loads of buildings using hourly weather data and detailed building envelope specifications.

## Overview

This project implements a steady-state heat balance method to calculate:
- **Peak heating loads** using 0.4th percentile design day conditions
- **Peak cooling loads** using 99.6th percentile design day conditions
- Transmission losses through walls, roofs, windows, and ground-contact elements
- Ventilation and infiltration loads with heat recovery
- Solar gains through windows
- Internal gains from occupants, equipment, and lighting

## Project Structure

```
├── main.py          # Main simulation script
├── main_annual.py   # Annual energy analysis
├── config.py        # Building parameters and constants
├── building.py      # Data classes for planes, air systems, internal gains
├── physics.py       # Heat transfer calculations
├── weather.py       # EPW weather file parser
├── visualize.py     # Plotting functions
├── weather_files/   # EPW weather data (not tracked)
└── plots/           # Generated visualizations (not tracked)
```

## Requirements

- Python 3.8+
- pandas
- numpy
- matplotlib

Install dependencies:
```bash
pip install pandas numpy matplotlib
```

## Weather Data

This simulation uses EnergyPlus Weather (EPW) files. Download TMY weather data from:
- [Climate.OneBuilding.Org](https://climate.onebuilding.org/)
- [EnergyPlus Weather Data](https://energyplus.net/weather)

Place EPW files in `weather_files/` directory. The default configuration uses Stockholm Arlanda weather data.

## Usage

Run the main simulation:
```bash
python main.py
```

This will:
1. Load and analyze weather data
2. Identify design heating day (0.4th percentile) and cooling day (99.6th percentile)
3. Calculate hourly heating and cooling loads for design days
4. Generate visualization plots in `plots/`

## Building Configuration

Edit `config.py` to modify:

| Parameter | Description |
|-----------|-------------|
| `BUILDING_VOLUME` | Total building volume (m³) |
| `VENT_FLOW` | Mechanical ventilation rate (m³/s) |
| `HRV_EFF` | Heat recovery efficiency |
| `INFILTRATION_ACH` | Air changes per hour from infiltration |
| `T_HEAT` / `T_COOL` | Heating/cooling setpoints (°C) |
| `AG_WALL_U`, `AG_ROOF_U`, etc. | U-values for envelope elements (W/m²K) |

## Building Envelope

The model includes:
- Above-ground walls with sol-air temperature correction
- Pitched roof surfaces (25° tilt)
- Windows with solar heat gain coefficient (g-value) and shading factor
- Underground walls and floor slab with ground temperature boundary

## Output

The simulation generates:
- Console output with weather summary, building envelope metrics, and peak loads
- Weather analysis plots (temperature, solar radiation, sun path)
- Design day analysis (hourly stacked bar charts, heat distribution pie charts)
- Peak heating load breakdown by building element

## Physics Model

### Heating Load
```
Q_heat = max(0, -Q_transmission - Q_air)
```
Uses outdoor air temperature (conservative: ignores solar gains)

### Cooling Load
```
Q_cool = max(0, Q_transmission + Q_air + Q_solar + Q_internal)
```
Uses sol-air temperature for opaque elements

### Sol-Air Temperature
```
T_sol = T_out + (α × I) / h_e
```
Where α is solar absorptance, I is incident solar radiation, and h_e is external surface heat transfer coefficient.

## License

MIT
