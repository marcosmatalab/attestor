import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ClassificationCard } from "@/components/ClassificationCard";
import { classification } from "./fixtures";

describe("ClassificationCard", () => {
  it("renders the exact checksum it is given (verbatim, never recomputed)", () => {
    const checksum = "deadbeefcafe0001deadbeefcafe0002deadbeefcafe0003deadbeefcafe0004";
    render(<ClassificationCard c={classification(checksum)} />);

    expect(screen.getByText(checksum)).toBeInTheDocument();
  });

  it("shows the risk tier from the data and its obligations", () => {
    render(<ClassificationCard c={classification("abc")} />);

    expect(screen.getByText("high")).toBeInTheDocument();
    expect(screen.getByText("Risk management system")).toBeInTheDocument();
    expect(screen.getByText("Art. 9")).toBeInTheDocument();
  });
});
