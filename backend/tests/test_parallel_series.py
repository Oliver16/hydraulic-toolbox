import numpy as np
import pytest

from app.services.affinity import scale_curve
from app.services.combine import build_parallel, build_series
from app.services.curves import PumpCurve


def sample_curve():
    return PumpCurve(
        flow_si=np.array([0.0, 0.01, 0.02]),
        head_si=np.array([40.0, 30.0, 20.0]),
        efficiency=None,
        power=None,
        npshr=None,
        flow_unit="gpm",
        head_unit="ft",
        efficiency_unit=None,
        power_unit=None,
        npshr_unit=None,
    )


def test_parallel_combination_increases_flow():
    curve = sample_curve()
    aggregate = build_parallel([curve, curve], [1.0, 1.0], [1, 1])
    flow_domain = aggregate.flow_domain
    assert flow_domain[1] > curve.flow_si.max()
    head = aggregate.head(curve.flow_si.max() * 2)
    expected_head = curve.head_at(np.array([curve.flow_si.max()]))[0]
    assert head == pytest.approx(expected_head)


def test_series_combination_increases_head():
    curve = sample_curve()
    aggregate = build_series([curve, curve], [1.0, 1.0], [1, 1])
    head = aggregate.head(0.01)
    assert head > float(curve.head_si[1])

