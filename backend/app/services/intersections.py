from __future__ import annotations

from typing import Callable, Sequence

import numpy as np
from scipy.optimize import brentq


class IntersectionError(RuntimeError):
    pass


def find_operating_point(
    flow_domain: Sequence[float],
    pump_head: Callable[[float], float],
    system_head: Callable[[float], float],
) -> tuple[float, float]:
    q_min, q_max = float(min(flow_domain)), float(max(flow_domain))
    q_values = np.linspace(q_min, q_max, num=50)
    diffs = [pump_head(q) - system_head(q) for q in q_values]
    signs = np.sign(diffs)
    for i in range(len(signs) - 1):
        if signs[i] == 0:
            q = float(q_values[i])
            return q, float(pump_head(q))
        if signs[i] * signs[i + 1] < 0:
            lower = q_values[i]
            upper = q_values[i + 1]
            q = brentq(lambda x: pump_head(x) - system_head(x), lower, upper)
            return float(q), float(pump_head(q))
    raise IntersectionError("No intersection found within provided domain")

