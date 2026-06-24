import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { LanguageToggle } from "@/components/LanguageToggle";
import { LocaleProvider, useLocale } from "@/lib/i18n/LocaleProvider";

function Probe() {
  const { t } = useLocale();
  return <span data-testid="probe">{t("header.navClassify")}</span>;
}

afterEach(() => {
  try {
    window.localStorage.clear();
  } catch {
    // ignore
  }
});

describe("LocaleProvider / useLocale", () => {
  it("renders English without a provider (default context, no crash)", () => {
    render(<Probe />);
    expect(screen.getByTestId("probe")).toHaveTextContent("Classify");
  });

  it("renders the provided initialLocale", () => {
    render(
      <LocaleProvider initialLocale="es">
        <Probe />
      </LocaleProvider>,
    );
    expect(screen.getByTestId("probe")).toHaveTextContent("Clasificar");
  });

  it("the toggle switches the locale and persists it to localStorage", () => {
    render(
      <LocaleProvider>
        <LanguageToggle />
        <Probe />
      </LocaleProvider>,
    );
    expect(screen.getByTestId("probe")).toHaveTextContent("Classify"); // English by default

    fireEvent.click(screen.getByRole("button", { name: "ES" }));

    expect(screen.getByTestId("probe")).toHaveTextContent("Clasificar");
    expect(window.localStorage.getItem("attestor.locale")).toBe("es");
    expect(screen.getByRole("button", { name: "ES" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "EN" })).toHaveAttribute("aria-pressed", "false");
  });
});
