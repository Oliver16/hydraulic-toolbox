Tech Stack

Backend: Python 3.11, FastAPI, Pydantic v2, SQLModel/SQLAlchemy, Uvicorn, Celery, Redis, PostgreSQL

Frontend: Next.js 14 (App Router) + TypeScript, TailwindCSS, shadcn/ui, TanStack Query, react-hook-form + zod, Plotly.js

GIS/Math: numpy, pandas, scipy, pint

Reports: WeasyPrint (HTML→PDF)

Auth: email+password (JWT) with fastapi-users (or lightweight custom)

Maps (optional later): mapbox-gl

Packaging: Docker + docker-compose, Makefile, GitHub Actions (lint, test, build)

Testing: pytest + hypothesis

Domain Requirements

Build features to:

Upload/enter pump curves, design system head curve, and system head curves exported from hydraulic models (CSV).

Generate and visualize pump vs. system curves:

Single pump

Multiple pumps in parallel and in series

VFD turndown (affinity laws)

Model turndown BEP points

Show POR (default 70–120% of BEP flow, configurable) and AOR (default 50–120%, configurable) ranges

Modified curves for pump turndown/VFD setpoints

Compute intersections (operating points), duty+assist counts, wire-to-water power/efficiency, NPSHr margin if provided.

Persist inputs/outputs with complete audit trail (versioned models).

Export PDF report (inputs, plots, tables, conclusions) and CSV of computed curves.

Support unit safety using pint (US customary & SI), with unit selection in UI and consistent conversions.

Hydraulic Math Specs (implement exactly)

Pump curve input: At minimum columns: flow, head (units selectable). Optional: efficiency, power, npshr. Support piecewise CSV; fit smooth monotonic cubic spline (PCHIP) vs flow for head, efficiency, power.

Best Efficiency Point (BEP): argmax of efficiency(flow). If missing efficiency, approximate via parabola fit around minimum specific energy per flow segment; mark as “estimated”.

System head curve: 
𝐻
(
𝑄
)
=
𝐻
𝑠
+
𝐾
𝑄
2
+
∑
𝑖
𝑘
𝑖
𝑄
𝑛
𝑖
H(Q)=H
s
	​

+KQ
2
+∑
i
	​

k
i
	​

Q
n
i
	​

 (default just static head + KQ²). Allow CSV import of (Q,H) from hydraulic models; fit PCHIP to get continuous H(Q).

Affinity laws for VFD at speed ratio 
𝑟
=
𝑁
/
𝑁
𝑟
𝑎
𝑡
𝑒
𝑑
r=N/N
rated
	​

:

𝑄
𝑟
=
𝑟
⋅
𝑄
Q
r
	​

=r⋅Q

𝐻
𝑟
=
𝑟
2
⋅
𝐻
H
r
	​

=r
2
⋅H

𝑃
𝑟
=
𝑟
3
⋅
𝑃
P
r
	​

=r
3
⋅P
Implement scaling of pump curves about rated speed.

Multiple pumps:

Parallel: For a given head H, sum flows: 
𝑄
𝑡
𝑜
𝑡
(
𝐻
)
=
∑
𝑗
𝑄
𝑗
(
𝐻
)
Q
tot
	​

(H)=∑
j
	​

Q
j
	​

(H) (invert pump head→flow via spline root-finding).

Series: For a given flow Q, sum heads: 
𝐻
𝑡
𝑜
𝑡
(
𝑄
)
=
∑
𝑗
𝐻
𝑗
(
𝑄
)
H
tot
	​

(Q)=∑
j
	​

H
j
	​

(Q).

Operating point: intersection of pump aggregate curve and system curve via robust root solver (bracketing + Brent), return (Q*, H*) per configuration and per VFD setpoint.

POR & AOR bands: show as shaded ranges around BEP flow; defaults POR=[0.70, 1.20], AOR=[0.50, 1.20], but store per-pump overrides.

Interpolation/extrapolation: safe bounds; warn on extrapolation beyond data extents.

Units: project-level unit system; store raw values with pint Quantity, persist normalized SI internally, display per user setting.

API Design
Entities

Pump: id, name, rated_speed_rpm, unit_system, curve_points[{flow, head, efficiency?, power?, npshr?}], metadata

SystemCurve: id, name, static_head, K, extra_terms[{k, n}] OR csv_points[{flow, head}]

Scenario: id, name, pumps[{pump_id, count, arrangement("parallel"|"series"), vfd_speed_ratio in (0,1]}], system_curve_id, unit_system, settings{POR, AOR}, created_at, version

Result: id, scenario_id, points{labels & arrays}, operating_points[{config_label, speed_ratio, Q, H, eff?, power?}], report_paths{pdf, csv}

Routes (document with OpenAPI)

POST /api/pumps (JSON or CSV multipart)

GET /api/pumps/:id

POST /api/system-curves (JSON or CSV multipart)

POST /api/scenarios (define pump list, counts, arrangement, VFD speeds array)

POST /api/scenarios/:id/compute → sync if quick (<2s) else enqueue Celery, return task id + polling

GET /api/results/:id → JSON + signed URLs for plots/CSVs/PDF

GET /api/units → supported units & conversions

Auth: POST /auth/register, /auth/login, /auth/refresh

Frontend Pages

Dashboard (list Pumps, System Curves, Scenarios)

Pump Upload/Edit (CSV drag-drop; live plots; BEP auto-calc)

System Curve Builder (form for Hs, K, extra terms; or CSV import; preview)

Scenario Builder (select pumps, count, arrangement, VFD sliders or entries; unit system; POR/AOR)

Results View (Plotly charts: pump(s) curve(s), system curve(s), operating points, shaded POR/AOR; table with Q,H,Eff,Power; export buttons)

Report generation button → fetch PDF

Plots

Plotly, responsive, downloadable PNG/SVG.

Curves: each pump curve (rated & VFD variants), aggregate curve, system curve; highlight intersections.

Shaded vertical POR (BEP*POR range) and lighter AOR.

CSV Schemas

Pump CSV: header required flow,head optional efficiency,power,npshr, units row like # units: gpm, ft, %, hp, ft

System CSV: flow,head with units comment line.

Export CSV: dense sampled arrays for all curves + operating points.

Persistence

PostgreSQL schemas/tables via SQLModel; store original CSVs in /data/uploads; results in /data/exports.

Version every Pump and SystemCurve; Scenarios reference specific versions.

Validation

Backend validates monotonicity of pump head decreasing with flow; warn/tolerate small noise; fix via monotone spline.

Reject negative heads/flows; ensure unit parsing via pint.

Deliverables

Repo with full code; no placeholders.

docker-compose.yml (services: api, worker, redis, db, frontend)

Makefile targets: make up, make down, make seed, make test, make fmt, make report-demo

Seed sample files under samples/ for 2 pumps + 1 system curve

Unit tests covering:

Affinity scaling

Parallel/series combination

Intersection solver

POR/AOR masks

CSV parsers & units

File Tree (create exactly)
/frontend
  /app
    /(auth)/login/page.tsx
    /pumps/page.tsx
    /pumps/[id]/page.tsx
    /system-curves/page.tsx
    /scenarios/page.tsx
    /results/[id]/page.tsx
  /components/* (forms, charts)
  /lib/api.ts
  package.json
  tsconfig.json
  postcss.config.cjs
  tailwind.config.ts
  .env.local.example
/backend
  /app
    /core/units.py
    /core/schemas.py
    /db.py
    /models.py
    /routers/{pumps.py,system_curves.py,scenarios.py,results.py,auth.py}
    /services/{curves.py,combine.py,affinity.py,intersections.py,report.py,storage.py}
    /tasks/celery_app.py
    /tasks/compute.py
    main.py
  /tests/{test_affinity.py,test_parallel_series.py,test_intersections.py,test_por_aor.py,test_csv_parsers.py}
  pyproject.toml
  alembic.ini
  /alembic/*
/infrastructure
  docker-compose.yml
  nginx.conf
/ci
  github-actions.yml
/samples/{pump_A.csv,pump_B.csv,system_demo.csv}
/data/{uploads,exports}/.gitkeep
Makefile
README.md

Implementation Details (write all code)

curves.py: load CSV → pandas → assign units with pint → normalize to SI → build PCHIP splines for head(Q), eff(Q), power(Q). Provide sampling helpers sample_head(q_array).

affinity.py: functions to scale pump curve to speed ratio r; produce new splines.

combine.py:

aggregate_parallel([pump_spline_i], r_list, count_list) returns callable Q(H) via root on each pump’s H(Q) and summing.

aggregate_series([pump_spline_i], r_list, count_list) returns H(Q) sum callable.

intersections.py: robust solver to find Q* where H_pumps(Q)=H_system(Q); use bracketing [Q_min, Q_max] from overlapping domains.

report.py: Jinja2 HTML → WeasyPrint → PDF with plots saved from Plotly to_image on the frontend or matplotlib backend in API.

routers: implement endpoints exactly as specified; handle multipart CSV + JSON; persist to DB; enqueue Celery job for heavy computes.

Frontend forms: react-hook-form + zod for CSV or manual input; upload to API; display live preview charts using sampled arrays from /preview helper endpoints.

Plot overlays: rated curve solid, VFD dashed; POR (darker band), AOR (lighter band) centered around BEP flow vertical spans.

Results caching: store computed arrays as compressed JSON (or parquet) for quick reload.

Commands & Env

Provide .env.local.example and .env.example for API with POSTGRES_*, REDIS_URL, SECRET_KEY.

docker-compose up -d should start everything; initial alembic migration runs on API start.

make seed loads samples/*.csv as demo pumps/system curve and creates a demo scenario.

CI runs ruff or black, pytest, type checks (mypy or pyright for frontend).

Acceptance Tests (must pass)

Upload sample pumps and system curve → build scenario with 2×PumpA parallel, 1×PumpB off; VFD ratios [1.0, 0.9, 0.8] → compute → results include 3 operating points and plots render.

POR/AOR bands show correctly around BEP for each pump; legend entries present.

Export buttons produce valid PDF and CSV.

Unit switching between GPM/ft and L/s/m renders same physical points.

Generate all files and code now, with no placeholders or “fill in later” comments.
