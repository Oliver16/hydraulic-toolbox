import pytest

from app.services.curves import compute_por_aor


def test_por_aor_ranges():
    ranges = compute_por_aor(0.1, (0.7, 1.2), (0.5, 1.2))
    assert ranges["por"] == pytest.approx((0.07, 0.12))
    assert ranges["aor"] == pytest.approx((0.05, 0.12))


def test_por_requires_positive_bep():
    try:
        compute_por_aor(0.0, (0.7, 1.2), (0.5, 1.2))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for zero BEP")

