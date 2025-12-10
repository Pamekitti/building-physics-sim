# BESTEST Case 600/900 - RC Model Parameters
# 3-resistance model following Gori (2017)

from config import (
    AREA_ROOF, AREA_WALL_N, AREA_WALL_S, AREA_WALL_E, AREA_WALL_W,
)

TOTAL_WALL_AREA = AREA_WALL_N + AREA_WALL_S + AREA_WALL_E + AREA_WALL_W

# Lightweight wall (Case 600)
WALL_R1_LW = 0.121 + 0.075  # R_si + R_plasterboard
WALL_R2_LW = 1.650 + 0.064  # R_fiberglass + R_wood
WALL_R3_LW = 0.034  # R_se
WALL_CA_LW = 950 * 840 * 0.012 / 1000  # C/A = rho * cp * d / 1000 [kJ/m²K]

# Heavyweight wall (Case 900)
WALL_R1_HW = 0.121 + 0.196  # R_si + R_concrete
WALL_R2_HW = 1.537 + 0.064  # R_foam + R_wood
WALL_R3_HW = 0.034  # R_se
WALL_CA_HW = 1400 * 1000 * 0.100 / 1000  # C/A = rho * cp * d / 1000 [kJ/m²K]

# Roof (same for both cases)
ROOF_R1 = 0.121 + 0.063  # R_si + R_plasterboard
ROOF_R2 = 2.794 + 0.136  # R_fiberglass + R_deck
ROOF_R3 = 0.034  # R_se
ROOF_CA_LW = 950 * 840 * 0.010 / 1000  # plasterboard only
ROOF_CA_HW = ROOF_CA_LW  # Same roof construction for both cases (per A.3.2.5)

# Total capacitance
C_WALL_LW = WALL_CA_LW * 1000 * TOTAL_WALL_AREA
C_WALL_HW = WALL_CA_HW * 1000 * TOTAL_WALL_AREA
C_ROOF_LW = ROOF_CA_LW * 1000 * AREA_ROOF
C_ROOF_HW = ROOF_CA_HW * 1000 * AREA_ROOF
