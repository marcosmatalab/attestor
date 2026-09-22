"""The HTTP surface: a thin adapter whose numbers must equal the engine's."""

import pytest
from fastapi.testclient import TestClient

from attestor.api.main import app
from attestor.classifier import (
    AnnexIIIArea,
    Role,
    SystemProfile,
    classify,
    load_bundle,
)

PROFILE = {"role": "provider", "annex_iii_area": "employment"}


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="module")
def engine_result():
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    return classify(profile, load_bundle("v2026-08"))


def test_bundles_are_listed_with_their_content_hashes(client: TestClient) -> None:
    body = client.get("/api/bundles").json()
    versions = {b["version"]: b["sha256"] for b in body["bundles"]}

    assert "v2026-08" in versions
    assert versions["v2026-08"] == load_bundle("v2026-08").sha256
    assert body["default"] in versions


def test_classify_matches_the_engine_exactly(client: TestClient, engine_result) -> None:
    """The API must not be able to disagree with the library."""
    body = client.post(
        "/api/classify", json={"profile": PROFILE, "bundle_version": "v2026-08"}
    ).json()

    assert body["checksum"] == engine_result.checksum
    assert body["risk"] == engine_result.risk.value
    assert body["bundle_sha256"] == engine_result.bundle_sha256


def test_unknown_bundle_is_404(client: TestClient) -> None:
    response = client.post("/api/classify", json={"profile": PROFILE, "bundle_version": "nope"})
    assert response.status_code == 404


def test_unknown_profile_field_is_rejected(client: TestClient) -> None:
    response = client.post("/api/classify", json={"profile": {**PROFILE, "wat": 1}})
    assert response.status_code == 422


def test_timeline_reports_both_scenarios(client: TestClient) -> None:
    body = client.post("/api/timeline", json=PROFILE).json()
    assert body["legal_text_risk"] == "high"
    assert body["obligations"]
    assert body["omnibus_status"]


def test_annex_iv_returns_a_validated_dossier(client: TestClient) -> None:
    body = client.post("/api/annex-iv", json={"profile": PROFILE}).json()

    assert body["dossier"]["sections"]
    assert len(body["dossier_sha256"]) == 64
    assert len(body["pdf_sha256"]) == 64


def test_annex_iv_refuses_a_deployer_with_422(client: TestClient) -> None:
    """Annex IV is a provider obligation; the API must not invent one."""
    response = client.post(
        "/api/annex-iv",
        json={"profile": {"role": "deployer", "annex_iii_area": "employment"}},
    )
    assert response.status_code == 422
    assert "provider obligation" in response.json()["detail"]


def test_governance_returns_all_three_views(client: TestClient) -> None:
    body = client.post("/api/governance", json={"profile": PROFILE}).json()

    assert body["iso42001"]["mappings"]
    assert body["fria"]["required"] is False
    assert body["log_retention"]


def test_demo_runs_the_whole_pipeline(client: TestClient, engine_result) -> None:
    body = client.post("/api/demo/run").json()

    assert body["classification"]["checksum"] == engine_result.checksum
    assert body["provenance"]["integrity_ok"] is True
    assert body["provenance"]["trusted"] is False
    assert body["ledger"]["verification"]["verified"] is True
    assert body["engine"]["llm_used"] is False


def test_ledger_verify_agrees_with_the_offline_verifier(client: TestClient) -> None:
    demo = client.post("/api/demo/run").json()["ledger"]
    body = client.post(
        "/api/ledger/verify",
        json={"records": demo["records"], "signed_root": demo["signed_root"]},
    ).json()

    assert body["integrity_ok"] is True
    assert body["signature_ok"] is True


def test_ledger_verify_detects_a_tampered_submission(client: TestClient) -> None:
    demo = client.post("/api/demo/run").json()["ledger"]
    records = [dict(r) for r in demo["records"]]
    records[0]["subject"] = "sys-9"

    body = client.post(
        "/api/ledger/verify",
        json={"records": records, "signed_root": demo["signed_root"]},
    ).json()

    assert body["integrity_ok"] is False
    assert body["signature_ok"] is True
