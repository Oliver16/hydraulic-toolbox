from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates"


def render_report(data: Dict[str, Any], output_pdf: Path) -> Path:
    TEMPLATE_PATH.mkdir(parents=True, exist_ok=True)
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_PATH)), autoescape=select_autoescape(["html", "xml"]))
    template = env.get_template("report.html")
    html = template.render(**data)
    HTML(string=html).write_pdf(str(output_pdf))
    return output_pdf

