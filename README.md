# Building Heating & Cooling Load Simulator

Steady-state and dynamic thermal modelling of a BESTEST Case 600 building using TMYx weather data for Glasgow.

## What this does

Calculates annual heating demand using two approaches:
1. **Steady-state model** - hourly heat balance with sol-air temperature
2. **3R-C RC model** - lumped capacitance for thermal mass effects (lightweight vs heavyweight construction)

Also runs sensitivity analysis on key parameters (insulation, infiltration, orientation, etc).

## Running

```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy pandas matplotlib
```

Then open `main.ipynb` and run cells in order.