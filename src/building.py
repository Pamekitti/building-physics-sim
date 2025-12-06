from dataclasses import dataclass


@dataclass
class Plane:
    name: str
    type: str
    area: float
    tilt: float
    azimuth: float
    r: float
    alpha: float = None
    epsilon: float = None
    g: float = None
    F_sh: float = 1.0

    def R(self):
        return self.r / self.area

    def is_opaque(self):
        return self.type == 'opaque'

    def is_window(self):
        return self.type == 'window'


@dataclass
class AirSide:
    volume: float
    vent_flow: float
    hrv_eff: float
    infiltration: float


@dataclass
class InternalGains:
    equipment: float = 0.0
    occupants: float = 0.0
    lighting: float = 0.0

    def total(self):
        return self.equipment + self.occupants + self.lighting
