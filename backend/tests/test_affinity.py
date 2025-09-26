import numpy as np

from app.services.affinity import scale_curve
from app.services.curves import PumpCurve


def build_curve():
    return PumpCurve(
        flow_si=np.array([0.0, 0.01, 0.02]),
        head_si=np.array([40.0, 30.0, 10.0]),
        efficiency=np.array([0.6, 0.75, 0.7]),
        power=np.array([1000.0, 1200.0, 1500.0]),
        npshr=None,
        flow_unit="gpm",
        head_unit="ft",
        efficiency_unit="%",
        power_unit="hp",
        npshr_unit=None,
    )


def test_affinity_scaling_flow():
    curve = build_curve()
    scaled = scale_curve(curve, 0.8)
    np.testing.assert_allclose(scaled.scaled_flow(), curve.flow_si * 0.8)
    np.testing.assert_allclose(scaled.scaled_head(), curve.head_si * 0.64)
    np.testing.assert_allclose(scaled.scaled_power(), curve.power * 0.512)

