from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=False), nullable=False))


class Pump(SQLModel, table=True):
    __tablename__ = "pumps"
    __table_args__ = (UniqueConstraint("pump_key", "version", name="uq_pump_version"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    pump_key: int = Field(index=True)
    version: int = Field(default=1, nullable=False)
    name: str
    rated_speed_rpm: float
    unit_system: str
    flow_unit: str
    head_unit: str
    efficiency_unit: Optional[str] = None
    power_unit: Optional[str] = None
    npshr_unit: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    curve_points: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=False), nullable=False))


class SystemCurve(SQLModel, table=True):
    __tablename__ = "system_curves"
    __table_args__ = (UniqueConstraint("curve_key", "version", name="uq_system_curve_version"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    curve_key: int = Field(index=True)
    version: int = Field(default=1)
    name: str
    unit_system: str
    static_head: float
    static_head_unit: str
    resistance_coefficient: float
    flow_unit: str
    head_unit: str
    extra_terms: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    csv_points: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=False), nullable=False))


class Scenario(SQLModel, table=True):
    __tablename__ = "scenarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    system_curve_id: int = Field(foreign_key="system_curves.id")
    pumps: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    unit_system: str
    por_default_low: float
    por_default_high: float
    aor_default_low: float
    aor_default_high: float
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=False), nullable=False))

    results: list["Result"] = Relationship(back_populates="scenario")


class Result(SQLModel, table=True):
    __tablename__ = "results"

    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_id: int = Field(foreign_key="scenarios.id", index=True)
    operating_points: Dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    csv_path: str
    pdf_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=False), nullable=False))

    scenario: Scenario = Relationship(back_populates="results")


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, sa_column=Column(String(255), unique=True, nullable=False))
    hashed_password: str = Field(sa_column=Column(String(255), nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=False), nullable=False))


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    token: str = Field(sa_column=Column(String(512), unique=True, nullable=False))
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))

