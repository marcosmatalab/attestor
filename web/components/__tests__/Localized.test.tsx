import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import { ClassificationCard } from "@/components/ClassificationCard";
import { ProvenanceCard } from "@/components/ProvenanceCard";
import { QuestionnaireForm } from "@/components/QuestionnaireForm";
import { LocaleProvider } from "@/lib/i18n/LocaleProvider";
import { classification, provenance } from "./fixtures";

function renderEs(ui: ReactNode) {
  return render(<LocaleProvider initialLocale="es">{ui}</LocaleProvider>);
}

describe("localized chrome", () => {
  it("translates the card title: English by default, Spanish under the provider", () => {
    const { unmount } = render(<ClassificationCard c={classification("abc")} />);
    expect(screen.getByText("Classification")).toBeInTheDocument();
    unmount();

    renderEs(<ClassificationCard c={classification("abc")} />);
    expect(screen.getByText("Clasificación")).toBeInTheDocument();
  });

  it("uses the official Spanish AI Act terminology for option labels (value unchanged)", () => {
    renderEs(<QuestionnaireForm onSubmit={() => {}} busy={false} />);
    const option = screen.getByRole("option", { name: "Garantía del cumplimiento del Derecho" });
    // The DISPLAYED label is the official term; the VALUE sent to the engine stays the key.
    expect(option).toHaveValue("law_enforcement");
  });
});

describe("engine output stays VERBATIM under the Spanish locale (honesty guard)", () => {
  it("keeps the C2PA verdict token UNTRUSTED untranslated", () => {
    renderEs(<ProvenanceCard prov={provenance(false)} />);
    expect(screen.getByText("Procedencia C2PA")).toBeInTheDocument(); // chrome -> Spanish
    expect(screen.getByText("signer untrusted")).toBeInTheDocument(); // verdict token -> verbatim
    expect(screen.getByText(provenance(false).headline).textContent).toContain("UNTRUSTED");
  });

  it("keeps the risk enum and the checksum verbatim", () => {
    const checksum = "cafe0001cafe0002cafe0003cafe0004cafe0005cafe0006cafe0007cafe0008";
    renderEs(<ClassificationCard c={classification(checksum)} />);
    expect(screen.getByText("Clasificación")).toBeInTheDocument(); // chrome -> Spanish
    expect(screen.getByText("high")).toBeInTheDocument(); // risk enum -> verbatim
    expect(screen.getByText(checksum)).toBeInTheDocument(); // checksum -> verbatim
  });
});
