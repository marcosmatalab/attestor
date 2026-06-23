# Attestor dashboard (F8)

A thin Next.js 16 (App Router, React 19) presentation layer over the Attestor engine. It
calls the FastAPI backend and renders the **real** outputs verbatim — risk and checksum,
dual legal-text vs Omnibus dates, the Annex IV scaffold, the ISO/IEC 42001 crosswalk, the
FRIA scaffold, and the C2PA + ledger verification. There is **no compliance logic in the
frontend**; every verdict comes from the engine.

## Develop

```bash
# 1. Backend (from the repo root)
uvicorn attestor.api.main:app --reload          # http://127.0.0.1:8000

# 2. Frontend (from web/)
npm install
npm run dev                                      # http://localhost:3000
```

The API base URL defaults to `http://127.0.0.1:8000`; override with
`NEXT_PUBLIC_API_BASE_URL`.

## Build / lint

```bash
npm run lint
npm run build      # Turbopack; also type-checks
```
