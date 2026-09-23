import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LedgerCard } from "@/components/LedgerCard";
import type { LedgerVerification } from "@/lib/api";

const base: LedgerVerification = {
  integrity_ok: true,
  signature_ok: true,
  has_timestamp: false,
  verified: true,
  tampered: false,
  untrusted_signer: false,
  signer_not_pinned: false,
  headline: "ledger VERIFIED (Merkle root intact, Ed25519 signature valid; signer pinned)",
};

function show(ledger: LedgerVerification) {
  render(<LedgerCard ledger={ledger} merkleRoot="ab" records={3} />);
}

describe("LedgerCard", () => {
  it("says verified only when the engine does", () => {
    show(base);
    expect(screen.getByText("verified")).toBeInTheDocument();
  });

  it("never calls an unpinned ledger tampered", () => {
    show({ ...base, verified: false, signer_not_pinned: true, headline: "ledger SIGNER NOT PINNED" });
    expect(screen.getByText("signer not pinned")).toBeInTheDocument();
    expect(screen.queryByText("tampered")).not.toBeInTheDocument();
  });

  it("never calls a foreign signer tampered", () => {
    show({ ...base, verified: false, untrusted_signer: true, headline: "ledger UNTRUSTED SIGNER" });
    expect(screen.getByText("untrusted signer")).toBeInTheDocument();
    expect(screen.queryByText("tampered")).not.toBeInTheDocument();
  });

  it("says tampered when the records do not hold together", () => {
    show({ ...base, verified: false, tampered: true, integrity_ok: false, headline: "ledger TAMPERED" });
    expect(screen.getByText("tampered")).toBeInTheDocument();
  });
});
