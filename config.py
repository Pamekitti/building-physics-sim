# Physical constants
RHO_AIR = 1.2
CP_AIR = 1005.0
H_E = 25.0

# BESTEST Case 600 geometry
FLOOR_AREA = 48.0
BUILDING_HEIGHT = 2.5
BUILDING_VOLUME = FLOOR_AREA * BUILDING_HEIGHT

# Ventilation
VENT_FLOW = 0.0
HRV_EFF = 0.0
INFILTRATION_ACH = 0.5

T_HEAT = 20.0
INTERNAL_GAIN_W = 200.0

# Surface properties
ALPHA = 0.6
EPSILON = 0.9
SHGC = 0.789

# Surface resistances
R_SI = 0.121
R_SE = 0.034

# Wall construction (lightweight)
WALL_LAYERS = {
    'internal_surface': {'d': None, 'k': None, 'r': 0.121},
    'plasterboard':     {'d': 0.012, 'k': 0.160, 'r': 0.075},
    'fiberglass':       {'d': 0.066, 'k': 0.040, 'r': 1.650},
    'wood_siding':      {'d': 0.009, 'k': 0.140, 'r': 0.064},
    'external_surface': {'d': None, 'k': None, 'r': 0.034},
}
WALL_R = sum(L['r'] for L in WALL_LAYERS.values())

# Roof construction
ROOF_LAYERS = {
    'internal_surface': {'d': None, 'k': None, 'r': 0.121},
    'plasterboard':     {'d': 0.010, 'k': 0.160, 'r': 0.063},
    'fiberglass':       {'d': 0.1118, 'k': 0.040, 'r': 2.795},
    'roof_deck':        {'d': 0.019, 'k': 0.140, 'r': 0.136},
    'external_surface': {'d': None, 'k': None, 'r': 0.034},
}
ROOF_R = sum(L['r'] for L in ROOF_LAYERS.values())

WINDOW_R = 0.333

# Areas
AREA_ROOF = 48.0
AREA_WALL_N = 20.0
AREA_WALL_S = 8.0
AREA_WALL_E = 15.0
AREA_WALL_W = 15.0
AREA_WINDOW = 12.0
