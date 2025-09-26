from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..core.schemas import ResultRead
from ..db import get_session
from ..models import Result

router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("/{result_id}", response_model=ResultRead)
def get_result(result_id: int, session: Session = Depends(get_session)):
    result = session.get(Result, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return ResultRead(
        id=result.id,
        scenario_id=result.scenario_id,
        operating_points=result.operating_points,
        csv_path=result.csv_path,
        pdf_path=result.pdf_path,
        created_at=result.created_at,
    )

