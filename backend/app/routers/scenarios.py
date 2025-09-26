from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..core.schemas import ResultRead, ScenarioCreate, ScenarioRead
from ..db import get_session
from ..models import Pump, Scenario, SystemCurve
from ..tasks.compute import compute_scenario

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])


def _serialize_payload(payload: ScenarioCreate) -> dict:
    return {
        "unit_system": payload.unit_system,
        "items": [cfg.model_dump() for cfg in payload.pumps],
        "por": payload.por_default,
        "aor": payload.aor_default,
    }


@router.post("", response_model=ScenarioRead, status_code=status.HTTP_201_CREATED)
def create_scenario(payload: ScenarioCreate, session: Session = Depends(get_session)):
    system_curve = session.exec(select(SystemCurve).where(SystemCurve.id == payload.system_curve_id)).first()
    if not system_curve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="System curve not found")
    for cfg in payload.pumps:
        pump = session.exec(select(Pump).where(Pump.id == cfg.pump_id)).first()
        if not pump:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pump {cfg.pump_id} not found")
    model = Scenario(
        name=payload.name,
        system_curve_id=payload.system_curve_id,
        pumps=_serialize_payload(payload),
        unit_system=payload.unit_system,
        por_default_low=payload.por_default[0],
        por_default_high=payload.por_default[1],
        aor_default_low=payload.aor_default[0],
        aor_default_high=payload.aor_default[1],
    )
    session.add(model)
    session.commit()
    session.refresh(model)
    return ScenarioRead(
        id=model.id,
        name=model.name,
        system_curve_id=model.system_curve_id,
        system_curve_version=payload.system_curve_version,
        pumps=payload.pumps,
        unit_system=model.unit_system,
        por_default=(model.por_default_low, model.por_default_high),
        aor_default=(model.aor_default_low, model.aor_default_high),
        created_at=model.created_at,
    )


@router.post("/{scenario_id}/compute")
def compute(scenario_id: int, session: Session = Depends(get_session)):
    scenario = session.get(Scenario, scenario_id)
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    async_result = compute_scenario.delay(scenario_id)
    return {"task_id": async_result.id}

