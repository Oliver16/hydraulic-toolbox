from __future__ import annotations

from typing import List, Optional

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select

from ..core.schemas import CurvePoint, ExtraSystemTerm, SystemCurveCreate, SystemCurveRead
from ..core.units import convert_array
from ..db import get_session
from ..models import SystemCurve

router = APIRouter(prefix="/api/system-curves", tags=["system curves"])


def _convert_points(points: Optional[List[CurvePoint]], flow_unit: str, head_unit: str) -> dict | None:
    if not points:
        return None
    flows = np.array([pt.flow for pt in points], dtype=float)
    heads = np.array([pt.head for pt in points], dtype=float)
    return {
        "flow_si": convert_array(flows, flow_unit, "meter**3/second").tolist(),
        "head_si": convert_array(heads, head_unit, "meter").tolist(),
    }


@router.post("", response_model=SystemCurveRead, status_code=status.HTTP_201_CREATED)
def create_system_curve(payload: SystemCurveCreate, session: Session = Depends(get_session)):
    converted_points = _convert_points(payload.csv_points, payload.flow_unit, payload.head_unit)
    existing = session.exec(select(SystemCurve).where(SystemCurve.name == payload.name).order_by(SystemCurve.version.desc())).first()
    if existing:
        curve_key = existing.curve_key
        version = existing.version + 1
    else:
        max_key = session.exec(select(func.max(SystemCurve.curve_key))).one()[0]
        curve_key = (max_key or 0) + 1
        version = 1
    model = SystemCurve(
        curve_key=curve_key,
        version=version,
        name=payload.name,
        unit_system=payload.unit_system,
        static_head=convert_array([payload.static_head], payload.static_head_unit, "meter")[0],
        static_head_unit=payload.static_head_unit,
        resistance_coefficient=payload.resistance_coefficient,
        flow_unit=payload.flow_unit,
        head_unit=payload.head_unit,
        extra_terms={"terms": [term.model_dump() for term in payload.extra_terms]},
        csv_points=converted_points,
    )
    session.add(model)
    session.commit()
    session.refresh(model)
    return SystemCurveRead(
        id=model.id,
        version=model.version,
        name=model.name,
        unit_system=model.unit_system,
        static_head=payload.static_head,
        static_head_unit=payload.static_head_unit,
        resistance_coefficient=model.resistance_coefficient,
        flow_unit=model.flow_unit,
        head_unit=model.head_unit,
        extra_terms=payload.extra_terms,
        csv_points=payload.csv_points,
        created_at=model.created_at,
    )


@router.get("/{curve_id}", response_model=SystemCurveRead)
def get_system_curve(curve_id: int, session: Session = Depends(get_session)):
    model = session.get(SystemCurve, curve_id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="System curve not found")
    csv_points = None
    if model.csv_points:
        csv_points = [
            CurvePoint(flow=float(flow), head=float(head))
            for flow, head in zip(model.csv_points["flow_si"], model.csv_points["head_si"], strict=True)
        ]
    extra_terms = [
        ExtraSystemTerm(coefficient=term["coefficient"], exponent=term["exponent"])
        for term in model.extra_terms.get("terms", [])
    ]
    return SystemCurveRead(
        id=model.id,
        version=model.version,
        name=model.name,
        unit_system=model.unit_system,
        static_head=model.static_head,
        static_head_unit=model.static_head_unit,
        resistance_coefficient=model.resistance_coefficient,
        flow_unit=model.flow_unit,
        head_unit=model.head_unit,
        extra_terms=extra_terms,
        csv_points=csv_points,
        created_at=model.created_at,
    )



@router.get("", response_model=list[SystemCurveRead])
def list_system_curves(session: Session = Depends(get_session)):
    models = session.exec(select(SystemCurve)).all()
    results: list[SystemCurveRead] = []
    for model in models:
        csv_points = None
        if model.csv_points:
            csv_points = [
                CurvePoint(flow=float(flow), head=float(head))
                for flow, head in zip(model.csv_points["flow_si"], model.csv_points["head_si"], strict=True)
            ]
        extra_terms = [
            ExtraSystemTerm(coefficient=term["coefficient"], exponent=term["exponent"])
            for term in model.extra_terms.get("terms", [])
        ]
        results.append(
            SystemCurveRead(
                id=model.id,
                version=model.version,
                name=model.name,
                unit_system=model.unit_system,
                static_head=model.static_head,
                static_head_unit=model.static_head_unit,
                resistance_coefficient=model.resistance_coefficient,
                flow_unit=model.flow_unit,
                head_unit=model.head_unit,
                extra_terms=extra_terms,
                csv_points=csv_points,
                created_at=model.created_at,
            )
        )
    return results

