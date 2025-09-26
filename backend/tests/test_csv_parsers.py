import pandas as pd

from app.services.curves import create_pump_curve, load_pump_csv


PUMP_CSV = b"""# units: flow gpm, head ft, efficiency %, power hp\nflow,head,efficiency,power\n0,150,55,100\n500,140,70,120\n1000,120,75,160\n"""


def test_load_pump_csv():
    df, units = load_pump_csv(PUMP_CSV)
    assert list(df.columns) == ["flow", "head", "efficiency", "power"]
    assert units["flow"] == "gpm"
    curve = create_pump_curve(df, units)
    assert curve.flow_si.shape[0] == 3
    assert curve.head_si[0] > curve.head_si[-1]

