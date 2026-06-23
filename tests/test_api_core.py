"""Tests for the core API endpoints (classifier, timeline, Annex IV).

The decisive check: every endpoint returns exactly what the engine produces when called
directly (same checksum, same dates) — proof that the API is a thin wrapper, not a mock.
"""

from fastapi.testclient import TestClient

from attestor.annexiv import generate_dossier
from attestor.api.main import app
from attestor.classifier import SystemProfile, classify, compare_timelines, load_bundle

client = TestClient(app)
_BUNDLE = load_bundle("v2026-08")

_HIGH_PROVIDER = {"role": "provider", "annex_iii_area": "employment"}


def test_classify_returns_the_engine_output_verbatim() -> None:
    response = client.post("/api/classify", json=_HIGH_PROVIDER)
    assert response.status_code == 200
    body = response.json()

    direct = classify(SystemProfile(**_HIGH_PROVIDER), _BUNDLE)
    assert body["risk"] == direct.risk.value
    assert body["checksum"] == direct.checksum  # identical -> not a mock
    assert body["effective_dates"] == direct.effective_dates


def test_timeline_shows_dual_dates_and_the_caveat() -> None:
    response = client.post("/api/timeline", json=_HIGH_PROVIDER)
    assert response.status_code == 200
    body = response.json()

    direct = compare_timelines(SystemProfile(**_HIGH_PROVIDER))
    assert body["legal_text_risk"] == direct.legal_text_risk.value
    assert body["omnibus_status"] == direct.omnibus_status  # provisional caveat, verbatim
    # Every obligation carries BOTH dates (never a single date as "the" date).
    assert body["obligations"]
    for row in body["obligations"]:
        assert "legal_text_date" in row and "omnibus_date" in row


def test_annex_iv_matches_the_generator() -> None:
    response = client.post("/api/annex-iv", params={"system_name": "Demo"}, json=_HIGH_PROVIDER)
    assert response.status_code == 200
    body = response.json()

    profile = SystemProfile(**_HIGH_PROVIDER)
    direct = generate_dossier(profile, classify(profile, _BUNDLE), _BUNDLE, system_name="Demo")
    assert body["classification_checksum"] == direct.classification_checksum
    assert body["sections"]


def test_annex_iv_is_gated_for_a_deployer() -> None:
    deployer = {"role": "deployer", "annex_iii_area": "employment"}
    response = client.post("/api/annex-iv", json=deployer)
    assert response.status_code == 422
    # The engine's own message is surfaced, not a generic error.
    assert "provider" in response.json()["detail"]


def test_annex_iv_pdf_is_a_real_pdf() -> None:
    response = client.post("/api/annex-iv/pdf", json=_HIGH_PROVIDER)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
