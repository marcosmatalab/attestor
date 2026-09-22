/** The only place the frontend talks to the engine. */

import type { DemoResult, TimelineComparison } from "@/lib/types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`${path} failed: ${response.status} ${response.statusText}`);
  }
  return (await response.json()) as T;
}

export const api = {
  async demo(): Promise<DemoResult> {
    return postJson<DemoResult>("/api/demo/run", {});
  },

  async timeline(profile: Record<string, unknown>): Promise<TimelineComparison> {
    return postJson<TimelineComparison>("/api/timeline", profile);
  },
};
