# Physical constants
RHO_AIR = 1.2       # kg/m³
CP_AIR = 1005.0     # J/kg·K
H_E = 25.0          # external surface coefficient W/m²K

# BESTEST Case 600 geometry
FLOOR_AREA = 48.0
BUILDING_HEIGHT = 2.5
BUILDING_VOLUME = FLOOR_AREA * BUILDING_HEIGHT

# Ventilation params
VENT_FLOW = 0.0
HRV_EFF = 0.0
INFILTRATION_ACH = 0.5

# Setpoint
T_HEAT = 20.0

# Internal gains - 200W per BESTEST
INTERNAL_GAIN_W = 200.0

# Surface properties
ALPHA = 0.6
EPSILON = 0.9
SHGC = 0.789

# U-values from R-values
WALL_U = 1.0 / 1.944
ROOF_U = 1.0 / 3.147
WINDOW_U = 1.0 / 0.333
