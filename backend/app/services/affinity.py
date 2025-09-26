from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.interpolate import PchipInterpolator

from .curves import PumpCurve


@dataclass
class ScaledPumpCurve:
    base: PumpCurve
    speed_ratio: float

    def scaled_flow(self) -> np.ndarray:
        return self.base.flow_si * self.speed_ratio

    def scaled_head(self) -> np.ndarray:
        return self.base.head_si * (self.speed_ratio ** 2)

    def scaled_power(self) -> np.ndarray | None:
        if self.base.power is None:
            return None
        return self.base.power * (self.speed_ratio ** 3)

    def head_at(self, flow: np.ndarray) -> np.ndarray:
        interpolator = PchipInterpolator(self.scaled_flow(), self.scaled_head(), extrapolate=True)
        return interpolator(flow)

    def power_at(self, flow: np.ndarray) -> np.ndarray | None:
        power = self.scaled_power()
        if power is None:
            return None
        interpolator = PchipInterpolator(self.scaled_flow(), power, extrapolate=True)
        return interpolator(flow)

    def efficiency_at(self, flow: np.ndarray):
        if self.base.efficiency is None:
            return None
        interpolator = PchipInterpolator(self.scaled_flow(), self.base.efficiency, extrapolate=True)
        return interpolator(flow)


def scale_curve(curve: PumpCurve, ratio: float) -> ScaledPumpCurve:
    if ratio <= 0:
        raise ValueError("Speed ratio must be positive")
    return ScaledPumpCurve(base=curve, speed_ratio=ratio)

