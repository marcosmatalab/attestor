# HTTP API and dashboard (F8)

```bash
uvicorn attestor.api.main:app --reload
```

The API is a thin adapter and nothing more: it validates input, calls the engine and
serialises the result. It holds **no compliance logic** - every number a client sees
was produced by `attestor.classifier`, `attestor.annexiv`, `attestor.governance`,
`attestor.provenance` or `attestor.ledger`.

The dependency points one way. Engine packages never import `attestor.api`, and
`tests/test_architecture.py` enforces it, so the engine stays usable as a library and
testable without an HTTP client. `tests/test_api_routes.py` asserts that the API
returns exactly what the library returns, so the two cannot drift apart.

## Endpoints

| Method | Path | What it does |
|---|---|---|
| `GET` | `/health` | Liveness: service, version, environment |
| `GET` | `/api/bundles` | Every shipped bundle with its `sha256`, scenario and status |
| `POST` | `/api/classify` | Classify a profile under a bundle |
| `POST` | `/api/timeline` | The same profile under each timeline scenario |
| `POST` | `/api/annex-iv` | Annex IV dossier, citations validated, plus dossier and PDF digests |
| `POST` | `/api/governance` | ISO/IEC 42001 map, FRIA scaffold, log-retention duties |
| `POST` | `/api/ledger/verify` | Verify a submitted ledger (the same code path as the CLI) |
| `POST` | `/api/demo/run` | The whole pipeline end to end |

## Examples

```bash
curl -s localhost:8000/api/bundles | jq '.default, .bundles[].version'

curl -s localhost:8000/api/classify   -H 'content-type: application/json'   -d '{"profile": {"role": "provider", "annex_iii_area": "employment"}}' | jq .checksum

curl -s -XPOST localhost:8000/api/demo/run | jq '.provenance.headline, .ledger.verification.detail'
```

## Error behaviour

- an unknown bundle is **404**, naming the version;
- an unknown field on a profile is **422**. `extra="forbid"` is deliberate: a typo
  must not be silently ignored in a compliance questionnaire;
- a dossier the generator refuses to draw up is **422** carrying the specific reason,
  for instance that Annex IV is a provider obligation and this profile is a deployer.

## Dashboard

`web/` is a Next.js dashboard over the same API, with English and Spanish copy. It
holds no compliance logic either: every value on screen comes from the response, and
the regulatory status caveat is whatever the bundle `meta` said - which is why a
change in the law never means editing the frontend.

```bash
cd web
npm ci
npm run dev        # expects the API on http://127.0.0.1:8000
npm run lint && npm run typecheck && npm run build && npm test
```

The demo cards show C2PA integrity and signer trust on separate lines, for the same
reason the verifier separates them: an unrecognised signer must never render as a
tampered file.
