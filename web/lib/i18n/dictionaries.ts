/** UI copy in English and Spanish.
 *
 * Nothing here interprets the regulation. Every date, status and caveat the user
 * sees comes from the engine's bundle `meta`; these strings only label it. That
 * separation is why a regulatory change never means editing the frontend.
 */

export type Locale = "en" | "es";

export const LOCALES: Locale[] = ["en", "es"];
export const DEFAULT_LOCALE: Locale = "en";

export interface Dictionary {
  locale: Locale;
  nav: { home: string; demo: string };
  home: {
    title: string;
    tagline: string;
    deterministic: string;
    noLlm: string;
    runDemo: string;
    features: { title: string; body: string }[];
  };
  demo: {
    title: string;
    intro: string;
    run: string;
    running: string;
    failed: string;
    retry: string;
  };
  cards: {
    classification: string;
    risk: string;
    checksum: string;
    bundle: string;
    obligations: string;
    provenance: string;
    validationState: string;
    signer: string;
    ledger: string;
    merkleRoot: string;
    records: string;
    integrity: string;
    signature: string;
    annexIv: string;
    sections: string;
    citations: string;
  };
  timeline: {
    caption: string;
    thObligation: string;
    thLegalText: string;
    thOmnibus: string;
    notApplicable: string;
  };
  status: {
    verified: string;
    tampered: string;
    untrusted: string;
    trusted: string;
    provisionalBanner: string;
  };
}

const en: Dictionary = {
  locale: "en",
  nav: { home: "Overview", demo: "Live demo" },
  home: {
    title: "Attestor",
    tagline:
      "A deterministic EU AI Act compliance engine with an offline-verifiable cryptographic ledger.",
    deterministic: "Same input, same output, same checksum — every time.",
    noLlm: "No LLM touches the classification decision. A test enforces it.",
    runDemo: "Run the demo",
    features: [
      {
        title: "Deterministic classification",
        body: "A rule engine over a versioned regulatory bundle resolves the risk tier, the obligations and the date each one applies from.",
      },
      {
        title: "Annex IV dossier",
        body: "Every citation is validated against the bundle: a reference that does not resolve is rejected, never rendered.",
      },
      {
        title: "C2PA Content Credentials",
        body: "Signed outputs report integrity and signer trust as two separate axes, so an unknown signer never looks like a tampered file.",
      },
      {
        title: "Offline-verifiable ledger",
        body: "Ed25519 over an RFC 6962 Merkle root. A third party verifies it with no network, no keys and no clone.",
      },
    ],
  },
  demo: {
    title: "The whole pipeline, end to end",
    intro:
      "Classify, draw up the Annex IV dossier, sign an output with C2PA, anchor all three in the ledger, then verify the ledger. No keys, no network.",
    run: "Run the demo",
    running: "Running…",
    failed: "The demo could not run.",
    retry: "Try again",
  },
  cards: {
    classification: "Classification",
    risk: "Risk tier",
    checksum: "Checksum",
    bundle: "Bundle",
    obligations: "Obligations",
    provenance: "C2PA provenance",
    validationState: "Validation state",
    signer: "Signer",
    ledger: "Ledger",
    merkleRoot: "Merkle root",
    records: "Records",
    integrity: "Integrity",
    signature: "Signature",
    annexIv: "Annex IV dossier",
    sections: "Sections",
    citations: "Validated citations",
  },
  timeline: {
    caption: "The same system under each timeline scenario.",
    thObligation: "Obligation",
    thLegalText: "As enacted (Reg. 2024/1689)",
    thOmnibus: "In force (Reg. 2026/1744)",
    notApplicable: "n/a",
  },
  status: {
    verified: "VERIFIED",
    tampered: "TAMPERED",
    untrusted: "SIGNER UNTRUSTED",
    trusted: "SIGNER TRUSTED",
    provisionalBanner:
      "The right-hand column is the law in force: Reg. (EU) 2026/1744 (Digital Omnibus on AI), binding since 27 July 2026. The left-hand column is Reg. (EU) 2024/1689 as originally enacted. Both are shown, because knowing what changed is part of the answer.",
  },
};

const es: Dictionary = {
  locale: "es",
  nav: { home: "Resumen", demo: "Demo en vivo" },
  home: {
    title: "Attestor",
    tagline:
      "Un motor determinista de cumplimiento del Reglamento de IA con un registro criptográfico verificable sin conexión.",
    deterministic: "La misma entrada produce la misma salida y el mismo checksum, siempre.",
    noLlm: "Ningún LLM interviene en la decisión de clasificación. Hay un test que lo impide.",
    runDemo: "Ejecutar la demo",
    features: [
      {
        title: "Clasificación determinista",
        body: "Un motor de reglas sobre un paquete normativo versionado resuelve el nivel de riesgo, las obligaciones y la fecha desde la que se aplica cada una.",
      },
      {
        title: "Expediente del Anexo IV",
        body: "Cada cita se valida contra el paquete: una referencia que no resuelve se rechaza, nunca se muestra.",
      },
      {
        title: "Credenciales de contenido C2PA",
        body: "Las salidas firmadas informan de la integridad y de la confianza en el firmante como dos ejes distintos, para que un firmante desconocido nunca parezca un fichero manipulado.",
      },
      {
        title: "Registro verificable sin conexión",
        body: "Ed25519 sobre una raíz Merkle RFC 6962. Un tercero lo verifica sin red, sin claves y sin clonar el repo.",
      },
    ],
  },
  demo: {
    title: "El proceso completo, de principio a fin",
    intro:
      "Clasificar, generar el expediente del Anexo IV, firmar una salida con C2PA, anclar las tres cosas en el registro y verificarlo. Sin claves y sin red.",
    run: "Ejecutar la demo",
    running: "Ejecutando…",
    failed: "No se pudo ejecutar la demo.",
    retry: "Reintentar",
  },
  cards: {
    classification: "Clasificación",
    risk: "Nivel de riesgo",
    checksum: "Checksum",
    bundle: "Paquete normativo",
    obligations: "Obligaciones",
    provenance: "Procedencia C2PA",
    validationState: "Estado de validación",
    signer: "Firmante",
    ledger: "Registro",
    merkleRoot: "Raíz Merkle",
    records: "Registros",
    integrity: "Integridad",
    signature: "Firma",
    annexIv: "Expediente del Anexo IV",
    sections: "Secciones",
    citations: "Citas validadas",
  },
  timeline: {
    caption: "El mismo sistema bajo cada escenario de calendario.",
    thObligation: "Obligación",
    thLegalText: "Texto original (Regl. 2024/1689)",
    thOmnibus: "En vigor (Regl. 2026/1744)",
    notApplicable: "n/d",
  },
  status: {
    verified: "VERIFICADO",
    tampered: "MANIPULADO",
    untrusted: "FIRMANTE NO CONFIABLE",
    trusted: "FIRMANTE CONFIABLE",
    provisionalBanner:
      "La columna de la derecha es el derecho vigente: Regl. (UE) 2026/1744 (Omnibus Digital sobre IA), vinculante desde el 27 de julio de 2026. La de la izquierda es el Regl. (UE) 2024/1689 en su texto original. Se muestran las dos, porque saber qué cambió forma parte de la respuesta.",
  },
};

const DICTIONARIES: Record<Locale, Dictionary> = { en, es };

export function getDictionary(locale: string | undefined): Dictionary {
  if (locale && locale in DICTIONARIES) {
    return DICTIONARIES[locale as Locale];
  }
  return DICTIONARIES[DEFAULT_LOCALE];
}
