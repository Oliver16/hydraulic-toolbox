from app.services.intersections import IntersectionError, find_operating_point


def test_intersection_basic():
    def pump_head(flow: float) -> float:
        return 50 - 10 * flow

    def system_head(flow: float) -> float:
        return 10 + 5 * flow

    q, h = find_operating_point([0.0, 4.0], pump_head, system_head)
    assert round(q, 3) == 2.667
    assert round(h, 2) == 23.33


def test_no_intersection():
    def pump_head(flow: float) -> float:
        return 20.0

    def system_head(flow: float) -> float:
        return 30.0

    try:
        find_operating_point([0.0, 1.0], pump_head, system_head)
    except IntersectionError:
        pass
    else:
        raise AssertionError("Expected IntersectionError")

