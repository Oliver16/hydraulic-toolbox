from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from .units import UnitSystem


class CurvePoint(BaseModel):
    flow: float
    head: float
    efficiency: Optional[float] = None
    power: Optional[float] = None
    npshr: Optional[float] = None

    @field_validator("flow", "head")
    @classmethod
    def ensure_non_negative(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Flow and head must be non-negative")
        return value


class PumpCreate(BaseModel):
    name: str
    rated_speed_rpm: float = Field(gt=0)
    unit_system: UnitSystem = "us"
    flow_unit: str
    head_unit: str
    efficiency_unit: str | None = None
    power_unit: str | None = None
    npshr_unit: str | None = None
    curve_points: List[CurvePoint]
    metadata: dict | None = None


class PumpRead(PumpCreate):
    id: int
    version: int
    created_at: datetime


class PumpVersionRead(BaseModel):
    pump_id: int
    version: int
    created_at: datetime


class PumpReference(BaseModel):
    pump_id: int
    version: Optional[int] = None
    count: int = 1
    arrangement: str = Field(pattern="^(parallel|series)$")
    vfd_speed_ratio: float = Field(ge=0.3, le=1.2, default=1.0)
    por_range: tuple[float, float] | None = None
    aor_range: tuple[float, float] | None = None


class ExtraSystemTerm(BaseModel):
    coefficient: float
    exponent: float


class SystemCurveCreate(BaseModel):
    name: str
    unit_system: UnitSystem = "us"
    static_head: float = 0.0
    static_head_unit: str
    resistance_coefficient: float = 0.0
    flow_unit: str
    head_unit: str
    extra_terms: List[ExtraSystemTerm] = []
    csv_points: List[CurvePoint] | None = None


class SystemCurveRead(SystemCurveCreate):
    id: int
    version: int
    created_at: datetime


class ScenarioPumpConfig(BaseModel):
    pump_id: int
    version: Optional[int] = None
    count: int = Field(gt=0)
    arrangement: str = Field(pattern="^(parallel|series)$")
    vfd_speeds: List[float] = Field(default_factory=lambda: [1.0])


class ScenarioCreate(BaseModel):
    name: str
    system_curve_id: int
    system_curve_version: Optional[int] = None
    pumps: List[ScenarioPumpConfig]
    unit_system: UnitSystem = "us"
    por_default: tuple[float, float] = (0.7, 1.2)
    aor_default: tuple[float, float] = (0.5, 1.2)


class ScenarioRead(ScenarioCreate):
    id: int
    created_at: datetime


class OperatingPoint(BaseModel):
    configuration: str
    speed_ratio: float
    flow: float
    head: float
    efficiency: Optional[float] = None
    power: Optional[float] = None


class ResultRead(BaseModel):
    id: int
    scenario_id: int
    operating_points: List[OperatingPoint]
    csv_path: str
    pdf_path: str
    created_at: datetime


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: str
    password: str


class UserRead(BaseModel):
    id: int
    email: str
    created_at: datetime

