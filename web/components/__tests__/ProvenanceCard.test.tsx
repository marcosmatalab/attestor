import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ProvenanceCard } from "@/components/ProvenanceCard";
import { provenance } from "./fixtures";

describe("ProvenanceCard", () => {
  it("reports the signer untrusted when the engine says so — and NEVER trusted", () => {
    render(<ProvenanceCard prov={provenance(false)} />);

    expect(screen.getByText("signer untrusted")).toBeInTheDocument();
    expect(screen.queryByText("signer trusted")).not.toBeInTheDocument();
    // the honest qualifier is present and prominent
    expect(screen.getByText(/never shown without the trust qualifier/i)).toBeInTheDocument();
  });

  it("renders the engine headline verbatim (UNTRUSTED visible)", () => {
    const prov = provenance(false);
    render(<ProvenanceCard prov={prov} />);
    expect(screen.getByText(prov.headline)).toBeInTheDocument();
    expect(screen.getByText(prov.headline).textContent).toContain("UNTRUSTED");
  });

  it("shows a trusted signer only when the data actually says trusted", () => {
    render(<ProvenanceCard prov={provenance(true)} />);
    expect(screen.getByText("signer trusted")).toBeInTheDocument();
    expect(screen.queryByText("signer untrusted")).not.toBeInTheDocument();
  });
});
