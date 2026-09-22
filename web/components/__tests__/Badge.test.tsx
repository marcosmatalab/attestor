import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Badge, riskTone } from "@/components/Badge";

describe("Badge", () => {
  it("renders its tone as a class", () => {
    render(<Badge tone="ok">VERIFIED</Badge>);
    expect(screen.getByText("VERIFIED")).toHaveClass("badge", "badge-ok");
  });

  it("never renders prohibited or high as a neutral tone", () => {
    expect(riskTone("prohibited")).toBe("bad");
    expect(riskTone("high")).toBe("high");
  });

  it("maps the low tiers", () => {
    expect(riskTone("limited")).toBe("warn");
    expect(riskTone("minimal")).toBe("ok");
  });
});
