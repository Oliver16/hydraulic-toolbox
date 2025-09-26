from __future__ import annotations

from pathlib import Path

from .core.schemas import CurvePoint, PumpCreate, SystemCurveCreate
from .db import session_factory
from .models import Pump, SystemCurve
from .routers.pumps import _convert_points as convert_pump_points
from .routers.system_curves import _convert_points as convert_system_points
from .services.curves import load_pump_csv

SAMPLES = Path(__file__).resolve().parents[2] / "samples"


def seed() -> None:
    with session_factory() as session:  # type: ignore[call-arg]
        pump_files = ["pump_A.csv", "pump_B.csv"]
        pump_key_counter = 1
        for filename in pump_files:
            content = (SAMPLES / filename).read_bytes()
            df, units = load_pump_csv(content)
            curve_points = [
                CurvePoint(
                    flow=float(row.flow),
                    head=float(row.head),
                    efficiency=float(row.efficiency) if hasattr(row, "efficiency") else None,
                    power=float(row.power) if hasattr(row, "power") else None,
                )
                for row in df.itertuples(index=False)
            ]
            payload = PumpCreate(
                name=filename.split(".")[0],
                rated_speed_rpm=1780,
                unit_system="us",
                flow_unit=units.get("flow", "gpm"),
                head_unit=units.get("head", "ft"),
                efficiency_unit=units.get("efficiency", "%"),
                power_unit=units.get("power", "hp"),
                curve_points=curve_points,
            )
            converted = convert_pump_points(payload)
            pump = Pump(
                pump_key=pump_key_counter,
                version=1,
                name=payload.name,
                rated_speed_rpm=payload.rated_speed_rpm,
                unit_system=payload.unit_system,
                flow_unit=payload.flow_unit,
                head_unit=payload.head_unit,
                efficiency_unit=payload.efficiency_unit,
                power_unit=payload.power_unit,
                npshr_unit=payload.npshr_unit,
                metadata_json={},
                curve_points=converted,
            )
            session.add(pump)
            pump_key_counter += 1

        system_df, units = load_pump_csv((SAMPLES / "system_demo.csv").read_bytes())
        system_points = [CurvePoint(flow=float(row.flow), head=float(row.head)) for row in system_df.itertuples(index=False)]
        system_payload = SystemCurveCreate(
            name="Demo System",
            static_head=0.0,
            static_head_unit=units.get("head", "ft"),
            resistance_coefficient=1e-4,
            flow_unit=units.get("flow", "gpm"),
            head_unit=units.get("head", "ft"),
            unit_system="us",
            csv_points=system_points,
        )
        converted_system = convert_system_points(system_payload.csv_points, system_payload.flow_unit, system_payload.head_unit)
        system_curve = SystemCurve(
            curve_key=1,
            version=1,
            name=system_payload.name,
            unit_system=system_payload.unit_system,
            static_head=system_payload.static_head,
            static_head_unit=system_payload.static_head_unit,
            resistance_coefficient=system_payload.resistance_coefficient,
            flow_unit=system_payload.flow_unit,
            head_unit=system_payload.head_unit,
            extra_terms={"terms": []},
            csv_points=converted_system,
        )
        session.add(system_curve)
        session.commit()


if __name__ == "__main__":
    seed()
