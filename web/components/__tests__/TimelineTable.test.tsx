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

  it("surfaces the engine's status note verbatim", () => {
    render(<TimelineTable timeline={timeline()} />);
    expect(screen.getByText(/In force since 2026-07-27/i)).toBeInTheDocument();
  });
});
