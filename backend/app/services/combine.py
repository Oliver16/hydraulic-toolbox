from __future__ import annotations

from typing import Callable, Sequence

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

from .affinity import ScaledPumpCurve
from .curves import PumpCurve


class AggregateCurve:
    def __init__(self, flow_domain: tuple[float, float], head: Callable[[float], float]):
        self.flow_domain = flow_domain
        self.head = head


def _scaled(curves: Sequence[PumpCurve], ratios: Sequence[float]) -> list[ScaledPumpCurve]:
    return [ScaledPumpCurve(base, ratio) for base, ratio in zip(curves, ratios, strict=True)]


def build_parallel(curves: Sequence[PumpCurve], ratios: Sequence[float], counts: Sequence[int]) -> AggregateCurve:
    scaled = _scaled(curves, ratios)
    min_flow = sum(float(np.min(curve.scaled_flow())) * count for curve, count in zip(scaled, counts, strict=True))
    max_flow = sum(float(np.max(curve.scaled_flow())) * count for curve, count in zip(scaled, counts, strict=True))

    def total_flow_at_head(head: float) -> float:
        total = 0.0
        for curve, count in zip(scaled, counts, strict=True):
            flow_values = curve.scaled_flow()
            head_values = curve.scaled_head()
            head_curve = PchipInterpolator(flow_values, head_values, extrapolate=True)
            low_flow = float(flow_values[0])
            high_flow = float(flow_values[-1])

            def residual(flow: float) -> float:
                return float(head_curve(flow) - head)

            if head >= head_curve(low_flow):
                flow_at_head = low_flow
            elif head <= head_curve(high_flow):
                flow_at_head = high_flow
            else:
                flow_at_head = brentq(residual, low_flow, high_flow)
            total += flow_at_head * count
        return total

    def head_function(flow: float) -> float:
        low_head = min(float(np.min(curve.scaled_head())) for curve in scaled)
        high_head = max(float(np.max(curve.scaled_head())) for curve in scaled)

        def residual(head: float) -> float:
            return total_flow_at_head(head) - flow

        if flow <= min_flow:
            return high_head
        if flow >= max_flow:
            return low_head
        return brentq(residual, low_head, high_head)

    return AggregateCurve((min_flow, max_flow), head_function)


def build_series(curves: Sequence[PumpCurve], ratios: Sequence[float], counts: Sequence[int]) -> AggregateCurve:
    scaled = _scaled(curves, ratios)
    min_flow = max(float(np.min(curve.scaled_flow())) for curve in scaled)
    max_flow = min(float(np.max(curve.scaled_flow())) for curve in scaled)

    def head_function(flow: float) -> float:
        total = 0.0
        for curve, count in zip(scaled, counts, strict=True):
            interpolator = PchipInterpolator(curve.scaled_flow(), curve.scaled_head(), extrapolate=True)
            total += float(interpolator(flow)) * count
        return total

    return AggregateCurve((min_flow, max_flow), head_function)

