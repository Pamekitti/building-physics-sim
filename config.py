# Physical constants
RHO_AIR = 1.2
CP_AIR = 1005.0
H_E = 23.0  # external convection coeff

# Building
BUILDING_VOLUME = 17448.0
VENT_FLOW = 3.81  # m3/s
HRV_EFF = 0.79
INFILTRATION_ACH = 0.024

# Setpoints
T_HEAT = 21.0
T_COOL = 25.0

# Internal gains (kW)
EQUIP_GAIN = 29.1
OCC_GAIN = 18.6
LIGHT_GAIN = 11.8

# Material props
WALL_ALPHA = 0.3
ROOF_ALPHA = 0.7
EPSILON = 0.9
WINDOW_G = 0.52
WINDOW_F_SH = 0.71

# U-values
AG_WALL_U = 0.31
AG_ROOF_U = 0.09
WINDOW_U = 1.40
UG_WALL_U = 0.18
UG_FLOOR_U = 0.34

# Underground geometry
FLOOR_AREA = 1272.0  # Ground floor footprint for heat transfer calc
PERIMETER = 207.0
UG_WALL_HEIGHT = 2.0

# Total building area
ATEMP = 5816.0  # Total heated floor area (all floors)
