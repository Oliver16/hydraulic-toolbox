from __future__ import annotations

from typing import List

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select

from ..core.schemas import CurvePoint, PumpCreate, PumpRead
from ..core.units import convert_array
from ..db import get_session
from ..models import Pump

router = APIRouter(prefix="/api/pumps", tags=["pumps"])


def _convert_points(payload: PumpCreate) -> dict:
    flows = np.array([pt.flow for pt in payload.curve_points], dtype=float)
    heads = np.array([pt.head for pt in payload.curve_points], dtype=float)
    flow_si = convert_array(flows, payload.flow_unit, "meter**3/second")
    head_si = convert_array(heads, payload.head_unit, "meter")

    efficiency = [pt.efficiency for pt in payload.curve_points]
    eff_arr = None
    if any(v is not None for v in efficiency):
        eff_arr = np.array([v if v is not None else 0.0 for v in efficiency], dtype=float)
        if payload.efficiency_unit in {"%", "percent"}:
            eff_arr = eff_arr / 100.0

    power = [pt.power for pt in payload.curve_points]
    power_arr = None
    if any(v is not None for v in power):
        data = np.array([v if v is not None else 0.0 for v in power], dtype=float)
        if payload.power_unit:
            data = convert_array(data, payload.power_unit, "watt")
        power_arr = data

    npshr = [pt.npshr for pt in payload.curve_points]
    npshr_arr = None
    if any(v is not None for v in npshr):
        data = np.array([v if v is not None else 0.0 for v in npshr], dtype=float)
        if payload.npshr_unit:
            data = convert_array(data, payload.npshr_unit, "meter")
        npshr_arr = data

    return {
        "flow_si": flow_si.tolist(),
        "head_si": head_si.tolist(),
        "efficiency": eff_arr.tolist() if eff_arr is not None else None,
        "power": power_arr.tolist() if power_arr is not None else None,
        "npshr": npshr_arr.tolist() if npshr_arr is not None else None,
    }


@router.post("", response_model=PumpRead, status_code=status.HTTP_201_CREATED)
def create_pump(payload: PumpCreate, session: Session = Depends(get_session)):
    converted = _convert_points(payload)
    existing = session.exec(select(Pump).where(Pump.name == payload.name).order_by(Pump.version.desc())).first()
    if existing:
        pump_key = existing.pump_key
        version = existing.version + 1
    else:
        max_key = session.exec(select(func.max(Pump.pump_key))).one()[0]
        pump_key = (max_key or 0) + 1
        version = 1
    pump = Pump(
        pump_key=pump_key,
        version=version,
        name=payload.name,
        rated_speed_rpm=payload.rated_speed_rpm,
        unit_system=payload.unit_system,
        flow_unit=payload.flow_unit,
        head_unit=payload.head_unit,
        efficiency_unit=payload.efficiency_unit,
        power_unit=payload.power_unit,
        npshr_unit=payload.npshr_unit,
        metadata_json=payload.metadata or {},
        curve_points=converted,
    )
    session.add(pump)
    session.commit()
    session.refresh(pump)
    return PumpRead(
        id=pump.id,
        version=pump.version,
        name=pump.name,
        rated_speed_rpm=pump.rated_speed_rpm,
        unit_system=pump.unit_system,
        flow_unit=pump.flow_unit,
        head_unit=pump.head_unit,
        efficiency_unit=pump.efficiency_unit,
        power_unit=pump.power_unit,
        npshr_unit=pump.npshr_unit,
        curve_points=[CurvePoint(**cp.model_dump()) for cp in payload.curve_points],
        metadata=pump.metadata_json,
        created_at=pump.created_at,
    )


@router.get("/{pump_id}", response_model=PumpRead)
def get_pump(pump_id: int, session: Session = Depends(get_session)):
    pump = session.get(Pump, pump_id)
    if not pump:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pump not found")
    points = pump.curve_points
    eff_list = points.get("efficiency") or []
    curve_points: List[CurvePoint] = []
    for idx, (flow_si, head_si) in enumerate(zip(points["flow_si"], points["head_si"], strict=True)):
        eff = eff_list[idx] if idx < len(eff_list) else None
        curve_points.append(CurvePoint(flow=float(flow_si), head=float(head_si), efficiency=eff))
    return PumpRead(
        id=pump.id,
        version=pump.version,
        name=pump.name,
        rated_speed_rpm=pump.rated_speed_rpm,
        unit_system=pump.unit_system,
        flow_unit=pump.flow_unit,
        head_unit=pump.head_unit,
        efficiency_unit=pump.efficiency_unit,
        power_unit=pump.power_unit,
        npshr_unit=pump.npshr_unit,
        curve_points=curve_points,
        metadata=pump.metadata_json,
        created_at=pump.created_at,
    )



@router.get("", response_model=list[PumpRead])
def list_pumps(session: Session = Depends(get_session)):
    pumps = session.exec(select(Pump)).all()
    results: list[PumpRead] = []
    for pump in pumps:
        points = pump.curve_points
        curve_points = [
            CurvePoint(
                flow=float(flow),
                head=float(head),
                efficiency=(points.get("efficiency") or [None] * len(points["flow_si"]))[idx]
                if points.get("efficiency")
                else None,
            )
            for idx, (flow, head) in enumerate(zip(points["flow_si"], points["head_si"], strict=True))
        ]
        results.append(
            PumpRead(
                id=pump.id,
                version=pump.version,
                name=pump.name,
                rated_speed_rpm=pump.rated_speed_rpm,
                unit_system=pump.unit_system,
                flow_unit=pump.flow_unit,
                head_unit=pump.head_unit,
                efficiency_unit=pump.efficiency_unit,
                power_unit=pump.power_unit,
                npshr_unit=pump.npshr_unit,
                curve_points=curve_points,
                metadata=pump.metadata_json,
                created_at=pump.created_at,
            )
        )
    return results

