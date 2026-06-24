// i18n dictionaries. `en` is the source of truth; `es` is typed as `typeof en`, so tsc
// fails if the key sets diverge. Values are plain strings (no `as const`), so `es` may
// hold any string — parity is on keys, not on literal values.
//
// HONESTY RULE: this file holds ONLY chrome (titles, labels, questions, explanatory prose).
// Nothing the engine emits is translated — risk enums, checksums, dates, citation text,
// the C2PA verdict and its tokens (UNTRUSTED, Valid), ledger state, ISO ids, dossier/FRIA
// content — those are rendered verbatim from the API and never pass through here.

export type Locale = "en" | "es";

export const en = {
  header: {
    tagline: "deterministic EU AI Act engine",
    navClassify: "Classify",
    navDemo: "End-to-end demo",
    languageLabel: "Language",
  },
  honesty: {
    bannerLead: "Portfolio demonstration — not legal advice, not a compliance product.",
    bannerRest:
      'Every figure, date, checksum, and verdict below comes from a deterministic engine; the UI only displays it. No system is "compliant" or "certified" by this tool.',
  },
  classify: {
    title: "Classify an AI system",
    lead: "Answer the questionnaire; the deterministic engine resolves the risk tier, the applicable obligations and their effective dates, the Annex IV scaffold, and the governance artifacts.",
    emptyHint: "Submit the questionnaire to see the classification and its derived artifacts.",
  },
  questionnaire: {
    title: "Questionnaire",
    roleLabel: "Operator role",
    roleProvider: "Provider",
    roleDeployer: "Deployer",
    areaLabel: "Annex III high-risk area",
    areaNone: "none",
    areaBiometrics: "Biometrics",
    areaCriticalInfrastructure: "Critical infrastructure",
    areaEducation: "Education and vocational training",
    areaEmployment: "Employment and worker management",
    areaEssentialServices: "Essential services (public & private)",
    areaCreditScoring: "Creditworthiness / credit scoring",
    areaLifeHealthInsurance: "Life & health insurance",
    areaLawEnforcement: "Law enforcement",
    areaMigrationBorder: "Migration, asylum & border control",
    areaJusticeDemocracy: "Administration of justice & democratic processes",
    deployerTypeLabel: "Deployer type (relevant to the FRIA, Art. 27)",
    deployerTypePublicBody: "Public body",
    deployerTypePrivatePublicService: "Private provider of a public service",
    deployerTypeOther: "Other",
    signals: "Signals",
    signalAnnexIEmbedded: "Annex I embedded (product safety)",
    signalGpai: "General-purpose AI (GPAI)",
    signalInteracts: "Interacts with humans (Art. 50(1))",
    signalSynthetic: "Generates synthetic content (Art. 50(2))",
    submit: "Classify",
    submitting: "Classifying…",
  },
  classification: {
    title: "Classification",
    bundle: "Bundle",
    checksum: "Reproducible checksum",
    caption: "Applicable obligations and their legal-text effective dates",
    thObligation: "Obligation",
    thReference: "Reference",
    thEffective: "Effective (legal text)",
  },
  timeline: {
    title: "Dual timeline — legal text vs Digital Omnibus",
    caveat:
      'The binding legal text remains Reg. (EU) 2024/1689. The Omnibus column is provisional: {status}. Both dates are shown — never one as "the" date.',
    thObligation: "Obligation",
    thLegalText: "Legal text",
    thOmnibus: "Omnibus (provisional)",
  },
  annexiv: {
    title: "Annex IV technical documentation",
    notApplicable: "Not applicable to this classification.",
    validatedNote:
      '"Validated" means each citation resolves and traces to an obligation the classifier emitted — not that it substantiates a claim. The sections are a scaffold to complete.',
    noCitations: "No derived citations.",
  },
  crosswalk: {
    title: "ISO/IEC 42001 crosswalk",
    thObligation: "AI Act obligation",
    thIso: "Related ISO/IEC 42001 areas",
  },
  provenance: {
    title: "C2PA provenance",
    caveat:
      'Integrity ({state}) means the manifest is intact — it does not mean the signer is trusted. The demo’s dev certificate is on no C2PA trust list, so the signer is reported untrusted. "Valid" is never shown without the trust qualifier.',
    signer: "Signer",
    aiDisclosure: "AI disclosure",
  },
  ledger: {
    title: "Ledger (offline verification)",
    merkleRoot: "Merkle root",
    anchoredRecords: "Anchored records",
    caveat:
      "An append-only log with cryptographic integrity, verifiable offline by a third party — not a blockchain (no distribution, no consensus). The integrity and signature decide the verdict; TSA trust, when present, is reported separately.",
  },
  fria: {
    titleApplicable: "FRIA scaffold (Art. 27)",
    titleNotApplicable: "FRIA — fundamental rights impact assessment (Art. 27)",
    notApplicable: "Not applicable to this classification.",
    meta: "Trigger: {trigger} · {reference}, effective {date}",
  },
  demo: {
    title: "End-to-end demo",
    lead: "One example path for a high-risk provider: classify → Annex IV → sign an AI output (C2PA) → verify → anchor in the ledger → verify the ledger offline. Every output is produced live by the engine; signing and sealing use ephemeral dev keys generated per run.",
    run: "Run the demo",
    running: "Running the pipeline…",
    classification: "Classification",
    checksum: "Checksum",
    annexiv: "Annex IV",
    annexivSummary: "{name} — {n} sections",
  },
  common: {
    working: "Working…",
    requestFailed: "The request failed.",
  },
};

export const es: typeof en = {
  header: {
    tagline: "motor determinista del EU AI Act",
    navClassify: "Clasificar",
    navDemo: "Demo de extremo a extremo",
    languageLabel: "Idioma",
  },
  honesty: {
    bannerLead: "Demostración de portfolio — no es asesoramiento legal ni un producto de cumplimiento.",
    bannerRest:
      'Cada cifra, fecha, checksum y veredicto de abajo proviene de un motor determinista; la UI solo los muestra. Esta herramienta no declara ningún sistema "conforme" ni "certificado".',
  },
  classify: {
    title: "Clasifica un sistema de IA",
    lead: "Responde el cuestionario; el motor determinista resuelve el nivel de riesgo, las obligaciones aplicables y sus fechas de exigibilidad, el borrador del Anexo IV y los artefactos de gobernanza.",
    emptyHint: "Envía el cuestionario para ver la clasificación y sus artefactos derivados.",
  },
  questionnaire: {
    title: "Cuestionario",
    roleLabel: "Rol del operador",
    roleProvider: "Proveedor",
    roleDeployer: "Responsable del despliegue",
    areaLabel: "Ámbito de alto riesgo del Anexo III",
    areaNone: "ninguno",
    areaBiometrics: "Biometría",
    areaCriticalInfrastructure: "Infraestructuras críticas",
    areaEducation: "Educación y formación profesional",
    areaEmployment: "Empleo y gestión de los trabajadores",
    areaEssentialServices: "Servicios esenciales (públicos y privados)",
    areaCreditScoring: "Solvencia crediticia",
    areaLifeHealthInsurance: "Seguros de vida y de salud",
    areaLawEnforcement: "Garantía del cumplimiento del Derecho",
    areaMigrationBorder: "Migración, asilo y control de fronteras",
    areaJusticeDemocracy: "Administración de justicia y procesos democráticos",
    deployerTypeLabel: "Tipo de responsable del despliegue (relevante para la FRIA, art. 27)",
    deployerTypePublicBody: "Organismo público",
    deployerTypePrivatePublicService: "Proveedor privado de un servicio público",
    deployerTypeOther: "Otro",
    signals: "Señales",
    signalAnnexIEmbedded: "Integrado en producto del Anexo I (seguridad de productos)",
    signalGpai: "IA de uso general (GPAI)",
    signalInteracts: "Interactúa con personas (art. 50(1))",
    signalSynthetic: "Genera contenido sintético (art. 50(2))",
    submit: "Clasificar",
    submitting: "Clasificando…",
  },
  classification: {
    title: "Clasificación",
    bundle: "Paquete",
    checksum: "Checksum reproducible",
    caption: "Obligaciones aplicables y sus fechas de exigibilidad (texto legal)",
    thObligation: "Obligación",
    thReference: "Referencia",
    thEffective: "Exigible (texto legal)",
  },
  timeline: {
    title: "Calendario dual — texto legal vs Digital Omnibus",
    caveat:
      'El texto legal vinculante sigue siendo el Reg. (UE) 2024/1689. La columna Omnibus es provisional: {status}. Se muestran ambas fechas — nunca una como "la" fecha.',
    thObligation: "Obligación",
    thLegalText: "Texto legal",
    thOmnibus: "Omnibus (provisional)",
  },
  annexiv: {
    title: "Documentación técnica del Anexo IV",
    notApplicable: "No aplica a esta clasificación.",
    validatedNote:
      '"Validada" significa que cada cita resuelve y traza a una obligación que el clasificador emitió — no que la respalde. Las secciones son un borrador a completar.',
    noCitations: "Sin citas derivadas.",
  },
  crosswalk: {
    title: "Crosswalk con ISO/IEC 42001",
    thObligation: "Obligación del AI Act",
    thIso: "Áreas de ISO/IEC 42001 relacionadas",
  },
  provenance: {
    title: "Procedencia C2PA",
    caveat:
      'Integridad ({state}) significa que el manifiesto está intacto — no significa que el firmante sea de confianza. El certificado de dev de la demo no está en ninguna lista de confianza C2PA, así que el firmante se reporta como untrusted. "Valid" nunca se muestra sin el calificador de confianza.',
    signer: "Firmante",
    aiDisclosure: "Divulgación de IA",
  },
  ledger: {
    title: "Ledger (verificación offline)",
    merkleRoot: "Raíz de Merkle",
    anchoredRecords: "Registros anclados",
    caveat:
      "Un registro append-only con integridad criptográfica, verificable offline por un tercero — no es una blockchain (sin distribución ni consenso). La integridad y la firma deciden el veredicto; la confianza en la TSA, cuando la hay, se reporta por separado.",
  },
  fria: {
    titleApplicable: "Borrador de FRIA (art. 27)",
    titleNotApplicable: "FRIA — evaluación de impacto sobre los derechos fundamentales (art. 27)",
    notApplicable: "No aplica a esta clasificación.",
    meta: "Disparador: {trigger} · {reference}, exigible {date}",
  },
  demo: {
    title: "Demo de extremo a extremo",
    lead: "Un camino de ejemplo para un proveedor de alto riesgo: clasificar → Anexo IV → firmar una salida de IA (C2PA) → verificar → anclar en el ledger → verificar el ledger offline. Cada salida la produce el motor en vivo; la firma y el sellado usan claves de dev efímeras generadas por ejecución.",
    run: "Ejecutar la demo",
    running: "Ejecutando el pipeline…",
    classification: "Clasificación",
    checksum: "Checksum",
    annexiv: "Anexo IV",
    annexivSummary: "{name} — {n} secciones",
  },
  common: {
    working: "Procesando…",
    requestFailed: "La solicitud ha fallado.",
  },
};

const dictionaries: Record<Locale, typeof en> = { en, es };

function lookup(dict: typeof en, key: string): string | undefined {
  const value = key.split(".").reduce<unknown>((acc, part) => {
    if (acc && typeof acc === "object") {
      return (acc as Record<string, unknown>)[part];
    }
    return undefined;
  }, dict);
  return typeof value === "string" ? value : undefined;
}

function interpolate(template: string, vars: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (match, name: string) =>
    name in vars ? String(vars[name]) : match,
  );
}

/** Resolve a dotted key for `locale`, falling back to English, then to the key itself. */
export function translate(
  locale: Locale,
  key: string,
  vars?: Record<string, string | number>,
): string {
  const raw = lookup(dictionaries[locale], key) ?? lookup(dictionaries.en, key) ?? key;
  return vars ? interpolate(raw, vars) : raw;
}
