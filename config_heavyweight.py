# BESTEST Case 900 - Heavyweight building
# Same geometry as Case 600, different wall/roof construction

from config import (
    FLOOR_AREA, BUILDING_HEIGHT, BUILDING_VOLUME,
    AREA_ROOF, AREA_WALL_N, AREA_WALL_S, AREA_WALL_E, AREA_WALL_W, AREA_WINDOW,
    ALPHA, EPSILON, SHGC, WINDOW_R,
    R_SI, R_SE, H_E,
    RHO_AIR, CP_AIR,
    INFILTRATION_ACH, INTERNAL_GAIN_W
)

# Heavyweight wall (outside to inside):
# wood siding | foam insulation | concrete block | internal surface

WALL_LAYERS_HW = {
    'external_surface': {'d': None,  'k': None,  'rho': None,  'cp': None,  'r': 0.034},
    'wood_siding':      {'d': 0.009, 'k': 0.140, 'rho': 530,   'cp': 900,   'r': 0.064},
    'foam_insulation':  {'d': 0.0615,'k': 0.040, 'rho': 10,    'cp': 1400,  'r': 1.537},
    'concrete_block':   {'d': 0.100, 'k': 0.510, 'rho': 1400,  'cp': 1000,  'r': 0.196},
    'internal_surface': {'d': None,  'k': None,  'rho': None,  'cp': None,  'r': 0.121},
}

# Heavyweight roof (outside to inside):
# roof deck | fiberglass | concrete slab | internal surface

ROOF_LAYERS_HW = {
    'external_surface': {'d': None,  'k': None,  'rho': None,  'cp': None,  'r': 0.034},
    'roof_deck':        {'d': 0.019, 'k': 0.140, 'rho': 530,   'cp': 900,   'r': 0.136},
    'fiberglass':       {'d': 0.1118,'k': 0.040, 'rho': 12,    'cp': 840,   'r': 2.795},
    'concrete_slab':    {'d': 0.080, 'k': 1.130, 'rho': 1400,  'cp': 1000,  'r': 0.071},
    'internal_surface': {'d': None,  'k': None,  'rho': None,  'cp': None,  'r': 0.121},
}

WALL_R_HW = sum(L['r'] for L in WALL_LAYERS_HW.values())
ROOF_R_HW = sum(L['r'] for L in ROOF_LAYERS_HW.values())

TOTAL_WALL_AREA = AREA_WALL_N + AREA_WALL_S + AREA_WALL_E + AREA_WALL_W

# C = rho * cp * d * A
C_WALL_HW = WALL_LAYERS_HW['concrete_block']['rho'] * WALL_LAYERS_HW['concrete_block']['cp'] * WALL_LAYERS_HW['concrete_block']['d'] * TOTAL_WALL_AREA
C_ROOF_HW = ROOF_LAYERS_HW['concrete_slab']['rho'] * ROOF_LAYERS_HW['concrete_slab']['cp'] * ROOF_LAYERS_HW['concrete_slab']['d'] * AREA_ROOF

# Lightweight capacitances (plasterboard only)
C_WALL_LW = 950 * 840 * 0.012 * TOTAL_WALL_AREA
C_ROOF_LW = 950 * 840 * 0.010 * AREA_ROOF
