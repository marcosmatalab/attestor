import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TimelineTable } from "@/components/TimelineTable";
import { timeline } from "./fixtures";

describe("TimelineTable", () => {
  it("shows BOTH the legal-text and Omnibus dates, never one as 'the' date", () => {
    render(<TimelineTable timeline={timeline()} />);

    expect(screen.getByText("2026-08-02")).toBeInTheDocument(); // legal text
    expect(screen.getByText("2027-12-02")).toBeInTheDocument(); // Omnibus
  });

  it("surfaces the provisional Omnibus caveat verbatim", () => {
    render(<TimelineTable timeline={timeline()} />);
    expect(screen.getByText(/pending formal adoption \(provisional\)/i)).toBeInTheDocument();
  });
});
