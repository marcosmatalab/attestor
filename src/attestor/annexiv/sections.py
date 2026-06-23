"""The nine Annex IV points as fixed templates, and the obligation->section map.

IMPORTANT (honesty): the obligation->section mapping below is a *defensible
structuring* based on what each Annex IV point covers — it is NOT a mapping the
Regulation prescribes. Any obligation without an explicit mapping falls to the
appendix, so the generator never breaks on new or unmapped obligations.
"""

LEGAL_BASIS_OBLIGATION_ID = "art11_technical_documentation"
APPENDIX_NUMBER = "A"

_PLACEHOLDER = "[TO BE COMPLETED BY THE PROVIDER]"

# (number, title, guidance) — fixed template text from the Annex IV structure.
ANNEX_IV_SECTIONS: tuple[tuple[str, str, str], ...] = (
    (
        "1",
        "General description of the AI system",
        f"{_PLACEHOLDER} Intended purpose, provider identity, system versions, how the "
        "system interacts with hardware/software, the forms in which it is placed on the "
        "market, and the instructions for use.",
    ),
    (
        "2",
        "Description of the elements of the AI system and its development process",
        f"{_PLACEHOLDER} Development methods and steps, design specifications, system "
        "architecture, data requirements and provenance, human-oversight measures, "
        "validation and testing procedures, and cybersecurity measures.",
    ),
    (
        "3",
        "Monitoring, functioning and control of the AI system",
        f"{_PLACEHOLDER} Capabilities and limitations, accuracy and robustness, foreseeable "
        "unintended outcomes and sources of risk, human-oversight requirements, and the "
        "specifications of the input data.",
    ),
    (
        "4",
        "Appropriateness of the performance metrics",
        f"{_PLACEHOLDER} Justify why the chosen performance metrics are appropriate for this "
        "specific AI system.",
    ),
    (
        "5",
        "Risk management system (Article 9)",
        f"{_PLACEHOLDER} The risk-management system established, implemented and maintained "
        "in accordance with Article 9.",
    ),
    (
        "6",
        "Relevant changes through the system's lifecycle",
        f"{_PLACEHOLDER} Relevant changes made by the provider to the system throughout its "
        "lifecycle.",
    ),
    (
        "7",
        "Harmonised standards applied",
        f"{_PLACEHOLDER} The harmonised standards applied or, where they are not applied, the "
        "technical solutions adopted to meet the Chapter III, Section 2 requirements.",
    ),
    (
        "8",
        "EU declaration of conformity (Article 47)",
        f"{_PLACEHOLDER} Attach a copy of the EU declaration of conformity drawn up under "
        "Article 47.",
    ),
    (
        "9",
        "Post-market monitoring system (Article 72)",
        f"{_PLACEHOLDER} The post-market monitoring system and plan referred to in Article 72. "
        "(This bundle does not model Article 72 as a classifier obligation, so this section "
        "carries no derived citation — complete it from the system's monitoring plan.)",
    ),
)

APPENDIX_SECTION: tuple[str, str, str] = (
    APPENDIX_NUMBER,
    "Other applicable obligations (outside the Annex IV technical-documentation scope)",
    "Obligations that apply to this system but fall outside the Annex IV technical-"
    "documentation structure (e.g. quality management, registration, GPAI model "
    "obligations). Listed for completeness; each traces to an obligation the classifier "
    "emitted.",
)

# Defensible obligation -> Annex IV section(s) placement. Unmapped -> appendix.
OBLIGATION_SECTION_MAP: dict[str, tuple[str, ...]] = {
    "art9_risk_management": ("5",),
    "art10_data_governance": ("2",),
    "art12_record_keeping": ("3",),
    "art13_transparency_deployers": ("1", "3"),
    "art14_human_oversight": ("2", "3"),
    "art15_accuracy_robustness": ("3", "4"),
    "art43_conformity_assessment": ("7",),
    "art47_eu_declaration": ("8",),
    "art48_ce_marking": ("8",),
}
