"""Tests for the deterministic PDF export."""

from attestor.annexiv import generate_dossier, render_pdf
from attestor.classifier import AnnexIIIArea, Role, SystemProfile, classify, load_bundle


def _dossier():
    bundle = load_bundle("v2026-08")
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    return generate_dossier(profile, classify(profile, bundle), bundle)


def test_render_pdf_produces_a_pdf() -> None:
    pdf = render_pdf(_dossier())
    assert pdf[:5] == b"%PDF-"
    assert len(pdf) > 1000


def test_render_pdf_is_byte_deterministic() -> None:
    dossier = _dossier()
    assert render_pdf(dossier) == render_pdf(dossier)
