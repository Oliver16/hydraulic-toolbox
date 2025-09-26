# Hydraulic Toolbox

Hydraulic Toolbox is a full-stack application for hydraulic pump and system curve analytics. It provides CSV ingestion, VFD affinity scaling, multi-pump aggregation, and automated PDF/CSV reporting.

## Features

- FastAPI backend with SQLModel persistence, JWT authentication, and Celery-powered compute tasks.
- Pump ingestion with unit conversion using pint and monotonic PCHIP spline fitting.
- System curve builder supporting analytical coefficients or CSV imports.
- Scenario planner with VFD setpoints, POR/AOR calculations, and operating point solvers.
- Next.js 14 frontend with Tailwind CSS, shadcn-inspired UI components, Plotly charts, and TanStack Query data fetching.
- Docker-compose orchestration of API, Celery worker, PostgreSQL, Redis, and frontend.
- Automated PDF reporting via WeasyPrint and dense JSON/CSV exports.
- Extensive unit tests covering math utilities, CSV parsing, and operating point solvers.

## Getting Started

```bash
make up          # Build and start the full stack
make down        # Stop and remove containers
make test        # Run backend unit tests
make fmt         # Auto-format backend sources
make seed        # Load sample pumps and system curve into the database
make report-demo # Render a sample PDF report
```

Set environment variables by copying the provided examples:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

Then install dependencies locally if desired:

```bash
cd backend && pip install -e .[test,dev]
cd frontend && npm install
```

Run the backend locally:

```bash
uvicorn app.main:app --reload
```

Run the frontend dev server:

```bash
npm run dev
```

## Testing

Backend tests are powered by `pytest` and `hypothesis` and can be executed with `make test`. Frontend type checking occurs via the GitHub Actions workflow.

## License

MIT
