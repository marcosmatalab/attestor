import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FALLBACK_STATUS, TimelineTable } from "@/components/TimelineTable";
import { getDictionary } from "@/lib/i18n/dictionaries";
import { OBLIGATIONS, OMNIBUS_STATUS } from "./fixtures";

describe("TimelineTable", () => {
  it("shows both scenario dates for every obligation", () => {
    render(<TimelineTable obligations={OBLIGATIONS} status={OMNIBUS_STATUS} />);

    expect(screen.getAllByText("2026-08-02")).toHaveLength(3);
    expect(screen.getByText("2027-12-02")).toBeInTheDocument();
  });

  it("renders the caveat the engine reported, not a literal of its own", () => {
    render(<TimelineTable obligations={OBLIGATIONS} status={OMNIBUS_STATUS} />);
    expect(screen.getByText(OMNIBUS_STATUS)).toBeInTheDocument();
  });

  it("falls back to a literal only when the engine reported nothing", () => {
    render(<TimelineTable obligations={OBLIGATIONS} status="   " />);
    expect(screen.getByText(FALLBACK_STATUS)).toBeInTheDocument();
  });

  it("marks a row whose dates diverge", () => {
    const { container } = render(<TimelineTable obligations={OBLIGATIONS} />);
    expect(container.querySelectorAll("tr.diverges")).toHaveLength(2);
  });

  it("renders an inapplicable obligation without inventing a date", () => {
    render(<TimelineTable obligations={OBLIGATIONS} />);
    expect(screen.getByText("n/a")).toBeInTheDocument();
  });

  it("translates its headings", () => {
    render(<TimelineTable obligations={OBLIGATIONS} locale="es" />);
    expect(screen.getByText(getDictionary("es").timeline.thObligation)).toBeInTheDocument();
  });
});
