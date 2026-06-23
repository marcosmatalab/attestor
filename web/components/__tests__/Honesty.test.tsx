import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnnexIvCard } from "@/components/AnnexIvCard";
import { HonestyBanner } from "@/components/HonestyBanner";

describe("honesty surfaces", () => {
  it("keeps the persistent portfolio / not-legal-advice banner", () => {
    render(<HonestyBanner />);

    expect(screen.getByText(/portfolio demonstration/i)).toBeInTheDocument();
    expect(screen.getByText(/not legal advice/i)).toBeInTheDocument();
  });

  it("shows a gated Annex IV as the engine's message, not a fabricated error", () => {
    const note = "Annex IV technical documentation is a provider obligation; deployers do not draw it up";
    render(<AnnexIvCard dossier={null} note={note} />);

    expect(screen.getByText(/provider obligation/i)).toBeInTheDocument();
  });
});
