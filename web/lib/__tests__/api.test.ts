import { afterEach, describe, expect, it, vi } from "vitest";
import { API_BASE_URL, api } from "@/lib/api";
import { DEMO_RESULT } from "@/components/__tests__/fixtures";

afterEach(() => vi.unstubAllGlobals());

describe("api.demo", () => {
  it("posts to the engine and returns the parsed result", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => DEMO_RESULT });
    vi.stubGlobal("fetch", fetchMock);

    await expect(api.demo()).resolves.toEqual(DEMO_RESULT);
    expect(fetchMock).toHaveBeenCalledWith(
      API_BASE_URL + "/api/demo/run",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("raises on a non-ok response instead of rendering nothing", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 503, statusText: "Service Unavailable" }),
    );
    await expect(api.demo()).rejects.toThrow("503");
  });
});
