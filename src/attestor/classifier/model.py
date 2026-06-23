"""Domain model for the classifier: questionnaire input and classification output.

The input (``SystemProfile``) is the structured questionnaire that drives the
deterministic rules. It is intentionally made of enums/booleans (no free text):
classification must be reproducible, so every signal that affects the outcome is
an explicit, typed field.
"""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, model_validator


class Role(StrEnum):
    """Whether the operator is the provider or the deployer of the system."""

    provider = "provider"
    deployer = "deployer"


class RiskTier(StrEnum):
    """The four EU AI Act risk tiers (the headline classification)."""

    prohibited = "prohibited"
    high = "high"
    limited = "limited"
    minimal = "minimal"


class ProhibitedPractice(StrEnum):
    """The eight prohibited practices of Art. 5(1) (legal text, no Omnibus delta)."""

    subliminal_manipulation = "subliminal_manipulation"  # 5(1)(a)
    exploit_vulnerabilities = "exploit_vulnerabilities"  # 5(1)(b)
    social_scoring = "social_scoring"  # 5(1)(c)
    predictive_policing_profiling = "predictive_policing_profiling"  # 5(1)(d)
    facial_scraping = "facial_scraping"  # 5(1)(e)
    emotion_recognition_work_education = "emotion_recognition_work_education"  # 5(1)(f)
    biometric_categorization_sensitive = "biometric_categorization_sensitive"  # 5(1)(g)
    realtime_remote_biometric_id = "realtime_remote_biometric_id"  # 5(1)(h)


class AnnexIIIArea(StrEnum):
    """The eight Annex III high-risk areas.

    Area 5 (essential services) is split into its sub-points because Art. 27
    (FRIA) names 5(b) credit scoring and 5(c) life/health insurance explicitly.
    """

    biometrics = "biometrics"  # Annex III(1)
    critical_infrastructure = "critical_infrastructure"  # Annex III(2)
    education = "education"  # Annex III(3)
    employment = "employment"  # Annex III(4)
    essential_services = "essential_services"  # Annex III(5)(a),(d)
    credit_scoring = "credit_scoring"  # Annex III(5)(b)
    life_health_insurance = "life_health_insurance"  # Annex III(5)(c)
    law_enforcement = "law_enforcement"  # Annex III(6)
    migration_border = "migration_border"  # Annex III(7)
    justice_democracy = "justice_democracy"  # Annex III(8)


class DeployerType(StrEnum):
    """Deployer category relevant to the FRIA (Art. 27) condition."""

    public_body = "public_body"
    private_public_service = "private_public_service"
    other = "other"


class ContentLifecycle(StrEnum):
    """Whether AI-generated content is newly produced or pre-existing (legacy).

    Carried in F1 but date-neutral: under the pure legal text all of Art. 50 is
    2026-08-02. The legacy/new transition split is a Digital Omnibus delta (F2).
    """

    new = "new"
    legacy = "legacy"


class SystemProfile(BaseModel):
    """Structured questionnaire answers for one AI system."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    role: Role

    # Prohibited practices (Art. 5)
    prohibited_practice: ProhibitedPractice | None = None

    # High-risk pathways
    annex_iii_area: AnnexIIIArea | None = None
    annex_i_embedded: bool = False
    deployer_type: DeployerType | None = None

    # Transparency triggers (Art. 50)
    interacts_with_humans: bool = False  # 50(1)
    generates_synthetic_content: bool = False  # 50(2)
    content_lifecycle: ContentLifecycle | None = None
    informs_emotion_biometric: bool = False  # 50(3)
    generates_deepfakes: bool = False  # 50(4)

    # General-purpose AI (transversal, Arts 51-55)
    is_gpai: bool = False
    is_gpai_systemic: bool = False

    # Digital Omnibus addition to Art. 5 (provisional, not yet in force): AI that
    # generates non-consensual intimate imagery (NCII) / nudifiers or CSAM. The
    # prohibition has a safe harbour — it does not bite where the system has
    # reasonable and adequate technical safeguards to reliably prevent it. These
    # fields are inert under the legal-text bundle, which does not reference them.
    generates_ncii_or_csam: bool = False
    ncii_csam_safeguards: bool = False

    @model_validator(mode="after")
    def _require_content_lifecycle(self) -> "SystemProfile":
        if self.generates_synthetic_content and self.content_lifecycle is None:
            raise ValueError(
                "content_lifecycle is required when generates_synthetic_content is true"
            )
        return self


class AppliedObligation(BaseModel):
    """A single obligation that applies to the system, with its effective date."""

    model_config = ConfigDict(frozen=True)

    id: str
    reference: str  # e.g. "Art. 9" — resolvable in the bundle (used by F3 citations)
    title: str
    effective_date: date


class Classification(BaseModel):
    """The deterministic classification result for a ``SystemProfile``."""

    model_config = ConfigDict(frozen=True)

    risk: RiskTier
    obligations: tuple[AppliedObligation, ...]
    bundle_version: str
    bundle_sha256: str  # content-addressed identity of the bundle
    checksum: str  # sha256 over canonical(answers + bundle_sha256 + result)

    @property
    def effective_dates(self) -> dict[str, str]:
        """Map of obligation id -> ISO effective date."""
        return {o.id: o.effective_date.isoformat() for o in self.obligations}
