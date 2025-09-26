from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

from ..core.units import convert_array


@dataclass
class PumpCurve:
    flow_si: np.ndarray
    head_si: np.ndarray
    efficiency: Optional[np.ndarray]
    power: Optional[np.ndarray]
    npshr: Optional[np.ndarray]
    flow_unit: str
    head_unit: str
    efficiency_unit: Optional[str]
    power_unit: Optional[str]
    npshr_unit: Optional[str]

    def head_at(self, flow: np.ndarray) -> np.ndarray:
        interpolator = PchipInterpolator(self.flow_si, self.head_si, extrapolate=True)
        return interpolator(flow)

    def efficiency_at(self, flow: np.ndarray) -> Optional[np.ndarray]:
        if self.efficiency is None:
            return None
        interpolator = PchipInterpolator(self.flow_si, self.efficiency, extrapolate=True)
        return interpolator(flow)

    def power_at(self, flow: np.ndarray) -> Optional[np.ndarray]:
        if self.power is None:
            return None
        interpolator = PchipInterpolator(self.flow_si, self.power, extrapolate=True)
        return interpolator(flow)


def _extract_units_from_comment(comment: str) -> dict[str, str]:
    parts = comment.replace("#", "").replace("units:", "").strip().split(",")
    mapping: dict[str, str] = {}
    for part in parts:
        if not part.strip():
            continue
        pieces = [p for p in part.strip().split(" ") if p]
        if len(pieces) != 2:
            continue
        name, value = pieces
        mapping[name.strip().lower()] = value.strip()
    return mapping


def load_pump_csv(content: bytes) -> tuple[pd.DataFrame, dict[str, str]]:
    buffer = io.StringIO(content.decode("utf-8"))
    units: dict[str, str] = {}
    rows = []
    reader = csv.reader(buffer)
    header: list[str] | None = None
    for row in reader:
        if not row:
            continue
        if row[0].startswith("#") and "units" in row[0].lower():
            units = _extract_units_from_comment(row[0])
            continue
        if header is None:
            header = [item.strip().lower() for item in row]
            continue
        rows.append(row)
    if header is None:
        raise ValueError("CSV must include a header row")
    df = pd.DataFrame(rows, columns=header)
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.dropna()
    df = df.sort_values("flow")
    if not (df["flow"].diff().fillna(1) > 0).all():
        raise ValueError("Flow values must be strictly increasing")
    return df, units


def create_pump_curve(df: pd.DataFrame, units: dict[str, str]) -> PumpCurve:
    flow_unit = units.get("flow", "gallon_us/minute")
    head_unit = units.get("head", "foot")
    efficiency_unit = units.get("efficiency")
    power_unit = units.get("power")
    npshr_unit = units.get("npshr")

    flow_si = convert_array(df["flow"], flow_unit, "meter**3/second")
    head_si = convert_array(df["head"], head_unit, "meter")

    efficiency = df.get("efficiency")
    if efficiency is not None:
        if efficiency_unit in {"%", "percent"}:
            efficiency_si = efficiency.to_numpy(dtype=float) / 100.0
        else:
            efficiency_si = efficiency.to_numpy(dtype=float)
    else:
        efficiency_si = None

    power = df.get("power")
    if power is not None and power_unit:
        power_si = convert_array(power, power_unit, "watt")
    elif power is not None:
        power_si = power.to_numpy(dtype=float)
    else:
        power_si = None

    npshr = df.get("npshr")
    if npshr is not None and npshr_unit:
        npshr_si = convert_array(npshr, npshr_unit, "meter")
    elif npshr is not None:
        npshr_si = npshr.to_numpy(dtype=float)
    else:
        npshr_si = None

    return PumpCurve(
        flow_si=np.asarray(flow_si, dtype=float),
        head_si=np.asarray(head_si, dtype=float),
        efficiency=np.asarray(efficiency_si, dtype=float) if efficiency_si is not None else None,
        power=np.asarray(power_si, dtype=float) if power_si is not None else None,
        npshr=np.asarray(npshr_si, dtype=float) if npshr_si is not None else None,
        flow_unit=flow_unit,
        head_unit=head_unit,
        efficiency_unit=efficiency_unit,
        power_unit=power_unit,
        npshr_unit=npshr_unit,
    )


def best_efficiency_point(curve: PumpCurve) -> tuple[float, float]:
    if curve.efficiency is not None and np.any(curve.efficiency > 0):
        idx = int(np.argmax(curve.efficiency))
        return float(curve.flow_si[idx]), float(curve.head_si[idx])
    energy = curve.head_si / np.clip(curve.flow_si, 1e-6, None)
    idx = int(np.argmin(energy))
    return float(curve.flow_si[idx]), float(curve.head_si[idx])


def sample_curve(curve: PumpCurve, num: int = 200) -> dict[str, np.ndarray]:
    flows = np.linspace(curve.flow_si.min(), curve.flow_si.max(), num=num)
    return {
        "flow": flows,
        "head": curve.head_at(flows),
        "efficiency": curve.efficiency_at(flows),
        "power": curve.power_at(flows),
    }


def compute_por_aor(bep_flow: float, por: tuple[float, float], aor: tuple[float, float]) -> dict[str, tuple[float, float]]:
    if bep_flow <= 0:
        raise ValueError("BEP flow must be positive")
    por_low, por_high = por
    aor_low, aor_high = aor
    return {
        "por": (bep_flow * por_low, bep_flow * por_high),
        "aor": (bep_flow * aor_low, bep_flow * aor_high),
    }

