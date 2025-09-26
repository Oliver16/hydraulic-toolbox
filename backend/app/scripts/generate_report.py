from __future__ import annotations

from pathlib import Path

from ..services.report import render_report


def main() -> None:
    output = Path("data/exports/demo_report.pdf")
    output.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "scenario": "Demo",
        "results": [
            {"configuration": "Pump A", "speed_ratio": 1.0, "flow": 0.1, "head": 30.0, "efficiency": 0.75, "power": 1200},
            {"configuration": "Pump B", "speed_ratio": 0.9, "flow": 0.08, "head": 28.0, "efficiency": 0.7, "power": 900},
        ],
    }
    render_report(data, output)
    print(f"Report generated at {output}")


if __name__ == "__main__":
    main()
