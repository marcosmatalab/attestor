"""AI Act obligations mapped onto ISO/IEC 42001 anchors.

Why this exists: an organisation that already runs an AI management system does
not want a second, parallel compliance programme. Mapping each obligation the
classifier emitted onto the 42001 clause that already owns it turns "23 articles"
into "the clauses you are already audited against, plus these gaps".

**This mapping is a defensible structuring, not a normative correspondence.**
ISO/IEC 42001 is a management-system standard and the AI Act is law; neither
declares the other's mapping. It is kept as data, in one table, so it can be
argued with — which is the only honest way to ship an opinion.

Obligations with no mapping are reported in ``unmapped_obligations`` rather than
silently dropped, so the view can never look more complete than it is.
"""

from attestor.classifier.model import Classification
from attestor.governance.model import ControlMapping, ManagementSystemMap

# obligation id -> (ISO/IEC 42001 anchor, its title, why this anchor)
ISO_42001_MAP: dict[str, tuple[str, str, str]] = {
    "art9_risk_management": (
        "6.1",
        "Actions to address risks and opportunities",
        "Art. 9 requires a continuous, documented risk management system over the "
        "system's lifecycle, which is what clause 6.1 plans and operates.",
    ),
    "art10_data_governance": (
        "A.7",
        "Data for AI systems",
        "Art. 10 governs training, validation and testing data quality; Annex A.7 "
        "is the control set for data acquisition, quality and provenance.",
    ),
    "art11_technical_documentation": (
        "7.5",
        "Documented information",
        "Art. 11 and Annex IV define the technical file; clause 7.5 governs how "
        "documented information is created, controlled and retained.",
    ),
    "art12_record_keeping": (
        "A.6.2.8",
        "AI system recording of event logs",
        "Art. 12 mandates automatic logging over the lifetime of the system.",
    ),
    "art13_transparency_deployers": (
        "A.8.2",
        "Information for interested parties",
        "Art. 13 is instructions-for-use owed to the deployer, i.e. information "
        "provided to a documented interested party.",
    ),
    "art14_human_oversight": (
        "A.9.2",
        "Human oversight of AI systems",
        "Art. 14 requires oversight measures designed into the system.",
    ),
    "art15_accuracy_robustness": (
        "A.6.2.4",
        "AI system verification and validation",
        "Art. 15 sets accuracy, robustness and cybersecurity targets that V&V "
        "activities are what actually demonstrate.",
    ),
    "art16_provider_obligations": (
        "5.3",
        "Organizational roles, responsibilities and authorities",
        "Art. 16 is the provider's umbrella duty; clause 5.3 assigns who owns it.",
    ),
    "art17_quality_management": (
        "4.4",
        "AI management system",
        "Art. 17 is a quality management system requirement and maps onto the AIMS "
        "itself, not onto a single control.",
    ),
    "art26_6_log_retention": (
        "A.6.2.8",
        "AI system recording of event logs",
        "Art. 26(6) is the deployer-side retention duty over the same logs.",
    ),
    "art27_fria": (
        "A.5.2",
        "AI system impact assessment process",
        "Art. 27 is a fundamental-rights impact assessment; A.5.2 is the process "
        "control that runs impact assessments.",
    ),
    "art43_conformity_assessment": (
        "9.2",
        "Internal audit",
        "Art. 43 internal control is the conformity route most Annex III systems "
        "take, and it is an internal audit activity in management-system terms.",
    ),
    "art47_eu_declaration": (
        "7.5",
        "Documented information",
        "The EU declaration of conformity is a controlled record.",
    ),
    "art48_ce_marking": (
        "8.1",
        "Operational planning and control",
        "Affixing the CE marking is an operational release gate.",
    ),
    "art49_registration": (
        "8.1",
        "Operational planning and control",
        "Registration in the EU database is a release precondition.",
    ),
    "art50_1_chatbot": (
        "A.8.2",
        "Information for interested parties",
        "Art. 50(1) is disclosure owed to the person interacting with the system.",
    ),
    "art50_2_marking": (
        "A.8.2",
        "Information for interested parties",
        "Art. 50(2) machine-readable marking is disclosure carried by the content.",
    ),
    "art50_3_emotion_biometric": (
        "A.8.2",
        "Information for interested parties",
        "Art. 50(3) is disclosure to the exposed person.",
    ),
    "art50_4_deepfake": (
        "A.8.2",
        "Information for interested parties",
        "Art. 50(4) is deep-fake disclosure to the audience.",
    ),
}


def map_to_iso42001(classification: Classification) -> ManagementSystemMap:
    """Map every obligation in ``classification`` onto its ISO/IEC 42001 anchor."""
    mappings: list[ControlMapping] = []
    unmapped: list[str] = []

    for obligation in classification.obligations:
        anchor = ISO_42001_MAP.get(obligation.id)
        if anchor is None:
            unmapped.append(obligation.id)
            continue
        clause, iso_title, rationale = anchor
        mappings.append(
            ControlMapping(
                obligation_id=obligation.id,
                reference=obligation.reference,
                title=obligation.title,
                effective_date=obligation.effective_date,
                iso_clause=clause,
                iso_title=iso_title,
                rationale=rationale,
            )
        )

    mappings.sort(key=lambda m: (m.iso_clause, m.obligation_id))
    return ManagementSystemMap(
        bundle_version=classification.bundle_version,
        bundle_sha256=classification.bundle_sha256,
        classification_checksum=classification.checksum,
        mappings=tuple(mappings),
        unmapped_obligations=tuple(sorted(unmapped)),
    )
