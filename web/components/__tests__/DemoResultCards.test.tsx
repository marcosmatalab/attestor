import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DemoResultCards } from "@/components/DemoResultCards";
import { DEMO_RESULT } from "./fixtures";

describe("DemoResultCards", () => {
  it("shows the reproducible classification checksum in full", () => {
    render(<DemoResultCards result={DEMO_RESULT} />);
    expect(screen.getByText(DEMO_RESULT.classification.checksum)).toBeInTheDocument();
  });

  it("shows the risk tier with the high-risk tone", () => {
    render(<DemoResultCards result={DEMO_RESULT} />);
    expect(screen.getByText("high")).toHaveClass("badge-high");
  });

  it("never reports an untrusted signer as verified", () => {
    render(<DemoResultCards result={DEMO_RESULT} />);
    const badge = screen.getByText("SIGNER UNTRUSTED");

    expect(badge).toHaveClass("badge-warn");
    expect(badge).not.toHaveClass("badge-ok");
  });

  it("states integrity and trust as two separate facts", () => {
    render(<DemoResultCards result={DEMO_RESULT} />);

    expect(screen.getByText("Valid")).toBeInTheDocument();
    expect(screen.getByText(DEMO_RESULT.provenance.headline)).toBeInTheDocument();
  });

  it("reports a verified ledger with its Merkle root", () => {
    render(<DemoResultCards result={DEMO_RESULT} />);

    expect(screen.getByText("VERIFIED")).toHaveClass("badge-ok");
    expect(screen.getByText(DEMO_RESULT.ledger.signed_root.merkle_root)).toBeInTheDocument();
  });

  it("reports a tampered ledger as tampered", () => {
    const tampered = {
      ...DEMO_RESULT,
      ledger: {
        ...DEMO_RESULT.ledger,
        verification: { ...DEMO_RESULT.ledger.verification, verified: false, integrity_ok: false },
      },
    };
    render(<DemoResultCards result={tampered} />);
    expect(screen.getByText("TAMPERED")).toHaveClass("badge-bad");
  });
});
