from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from sqlmodel import Session, select

from ..core.schemas import OperatingPoint
from ..models import Pump, Result, Scenario, SystemCurve
from ..services.combine import build_parallel, build_series
from ..services.curves import PumpCurve, best_efficiency_point
from ..services.intersections import IntersectionError, find_operating_point
from ..services.report import render_report
from ..services.storage import save_json
from ..db import session_factory
from .celery_app import celery_app


def _pump_curve_from_model(model: Pump) -> PumpCurve:
    data = model.curve_points
    return PumpCurve(
        flow_si=np.array(data["flow_si"], dtype=float),
        head_si=np.array(data["head_si"], dtype=float),
        efficiency=np.array(data.get("efficiency"), dtype=float) if data.get("efficiency") is not None else None,
        power=np.array(data.get("power"), dtype=float) if data.get("power") is not None else None,
        npshr=np.array(data.get("npshr"), dtype=float) if data.get("npshr") is not None else None,
        flow_unit=model.flow_unit,
        head_unit=model.head_unit,
        efficiency_unit=model.efficiency_unit,
        power_unit=model.power_unit,
        npshr_unit=model.npshr_unit,
    )


def _system_curve_function(model: SystemCurve):
    if model.csv_points:
        flow = np.array(model.csv_points["flow_si"], dtype=float)
        head = np.array(model.csv_points["head_si"], dtype=float)
        from scipy.interpolate import PchipInterpolator

        interpolator = PchipInterpolator(flow, head, extrapolate=True)
        return (float(flow.min()), float(flow.max())), lambda q: float(interpolator(q))

    static_head = model.static_head
    k = model.resistance_coefficient
    extra_terms = model.extra_terms or {}
    terms = [(term["coefficient"], term["exponent"]) for term in extra_terms.get("terms", [])]

    def head_function(flow: float) -> float:
        total = static_head + k * (flow ** 2)
        for coeff, exponent in terms:
            total += coeff * (flow ** exponent)
        return total

    return (0.0, 10.0), head_function


@celery_app.task(name="compute_scenario")
def compute_scenario(scenario_id: int) -> int:
    with session_factory() as session:  # type: ignore[call-arg]
        scenario = session.exec(select(Scenario).where(Scenario.id == scenario_id)).one()
        system_curve = session.exec(select(SystemCurve).where(SystemCurve.id == scenario.system_curve_id)).one()

        pumps: List[Dict[str, Any]] = scenario.pumps["items"]
        system_domain, system_head = _system_curve_function(system_curve)

        operating_points: List[Dict[str, Any]] = []
        for entry in pumps:
            pump_model = session.exec(select(Pump).where(Pump.id == entry["pump_id"])).one()
            curve = _pump_curve_from_model(pump_model)
            count = entry.get("count", 1)
            arrangement = entry.get("arrangement", "parallel")
            speeds = entry.get("vfd_speeds", [1.0])

            for ratio in speeds:
                if arrangement == "series":
                    aggregate = build_series([curve], [ratio], [count])
                else:
                    aggregate = build_parallel([curve], [ratio], [count])
                try:
                    q, h = find_operating_point(
                        flow_domain=np.linspace(aggregate.flow_domain[0], aggregate.flow_domain[1], 200),
                        pump_head=aggregate.head,
                        system_head=system_head,
                    )
                except IntersectionError:
                    continue
                eff = None
                if curve.efficiency is not None:
                    from scipy.interpolate import PchipInterpolator

                    eff_interp = PchipInterpolator(curve.flow_si * ratio, curve.efficiency, extrapolate=True)
                    eff = float(eff_interp(q / count if arrangement == "parallel" else q))
                power = None
                if curve.power is not None:
                    from scipy.interpolate import PchipInterpolator

                    scaled_power = curve.power * (ratio ** 3)
                    power_interp = PchipInterpolator(curve.flow_si * ratio, scaled_power, extrapolate=True)
                    power = float(power_interp(q / count if arrangement == "parallel" else q)) * count
                operating_points.append(
                    {
                        "configuration": f"{pump_model.name} x{count} {arrangement}",
                        "speed_ratio": ratio,
                        "flow": q,
                        "head": h,
                        "efficiency": eff,
                        "power": power,
                    }
                )

        payload = {"operating_points": operating_points, "computed_at": datetime.utcnow().isoformat()}
        json_path = save_json(f"scenario_{scenario_id}_results.json", payload)
        pdf_path = render_report(
            data={"scenario": scenario.name, "results": operating_points},
            output_pdf=Path(f"data/exports/scenario_{scenario_id}.pdf"),
        )

        result = Result(
            scenario_id=scenario_id,
            operating_points=operating_points,
            csv_path=f"files/{json_path.name}",
            pdf_path=f"files/{pdf_path.name}",
        )
        session.add(result)
        session.commit()
        session.refresh(result)
        return result.id

