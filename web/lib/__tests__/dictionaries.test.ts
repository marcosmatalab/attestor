import { describe, expect, it } from "vitest";
import { DEFAULT_LOCALE, LOCALES, getDictionary } from "@/lib/i18n/dictionaries";

describe("dictionaries", () => {
  it("falls back to the default locale for anything unknown", () => {
    expect(getDictionary("de").locale).toBe(DEFAULT_LOCALE);
    expect(getDictionary(undefined).locale).toBe(DEFAULT_LOCALE);
  });

  it("serves every declared locale", () => {
    for (const locale of LOCALES) {
      expect(getDictionary(locale).locale).toBe(locale);
    }
  });

  it("keeps the same keys in every locale, so no string can go missing", () => {
    const keysOf = (value: unknown, prefix = ""): string[] =>
      value && typeof value === "object" && !Array.isArray(value)
        ? Object.entries(value).flatMap(([k, v]) => [
            prefix + k,
            ...keysOf(v, prefix + k + "."),
          ])
        : [];

    expect(keysOf(getDictionary("es")).sort()).toEqual(keysOf(getDictionary("en")).sort());
  });

  it("describes the same number of features in every locale", () => {
    expect(getDictionary("es").home.features).toHaveLength(
      getDictionary("en").home.features.length,
    );
  });
});
