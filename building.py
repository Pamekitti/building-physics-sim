from dataclasses import dataclass
from typing import Optional


@dataclass
class Plane:
    name: str
    type: str
    area_m2: float
    tilt_deg: float
    azimuth_deg: float
    U: float
    alpha: Optional[float] = None
    epsilon: Optional[float] = None
    g: Optional[float] = None
    F_sh: float = 1.0
    ground_contact: bool = False

    def is_opaque(self):
        return self.type == 'opaque'

    def is_window(self):
        return self.type == 'window'


@dataclass
class AirSide:
    V_zone_m3: float
    Vdot_vent_m3s: float
    eta_HRV: float
    ACH_infiltration_h: float


@dataclass
class InternalGains:
    Q_equip_kW: float = 0.0
    Q_occ_kW: float = 0.0
    Q_light_kW: float = 0.0

    def total_kw(self):
        return self.Q_equip_kW + self.Q_occ_kW + self.Q_light_kW
