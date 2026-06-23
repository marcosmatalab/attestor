import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// globals:false means RTL does not auto-register cleanup; unmount between tests so the
// jsdom document does not accumulate renders (which would cause "multiple elements").
afterEach(() => {
  cleanup();
});
