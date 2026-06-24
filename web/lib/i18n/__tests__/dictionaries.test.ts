import { describe, expect, it } from "vitest";
import { en, es, translate } from "@/lib/i18n/dictionaries";

function keyPaths(obj: Record<string, unknown>, prefix = ""): string[] {
  return Object.entries(obj).flatMap(([k, v]) => {
    const path = prefix ? `${prefix}.${k}` : k;
    return v && typeof v === "object" ? keyPaths(v as Record<string, unknown>, path) : [path];
  });
}

describe("i18n dictionaries", () => {
  it("en and es have exactly the same set of keys", () => {
    expect(keyPaths(es).sort()).toEqual(keyPaths(en).sort());
  });

  it("translate() returns the string for the requested locale", () => {
    expect(translate("en", "questionnaire.title")).toBe("Questionnaire");
    expect(translate("es", "questionnaire.title")).toBe("Cuestionario");
    expect(translate("es", "questionnaire.areaLawEnforcement")).toBe(
      "Garantía del cumplimiento del Derecho",
    );
  });

  it("falls back to the key itself when it is absent in both locales", () => {
    // The es <-> en parity test guarantees the es-miss -> en-hit link is never needed for a
    // real key; an unknown key falls through es, then en, to the key string.
    expect(translate("es", "nonexistent.key")).toBe("nonexistent.key");
    expect(translate("en", "totally.unknown")).toBe("totally.unknown");
  });

  it("interpolates {vars}", () => {
    expect(translate("en", "demo.annexivSummary", { name: "Sys", n: 10 })).toBe(
      "Sys — 10 sections",
    );
    expect(translate("es", "demo.annexivSummary", { name: "Sys", n: 10 })).toBe(
      "Sys — 10 secciones",
    );
  });
});
