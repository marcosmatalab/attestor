"use client";

import { useState } from "react";
import { DemoResultCards } from "@/components/DemoResultCards";
import { api } from "@/lib/api";
import { getDictionary } from "@/lib/i18n/dictionaries";
import type { DemoResult } from "@/lib/types";

export default function DemoPage() {
  const t = getDictionary("en");
  const [result, setResult] = useState<DemoResult | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setRunning(true);
    setError(null);
    try {
      setResult(await api.demo());
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setRunning(false);
    }
  }

  return (
    <main>
      <h1>{t.demo.title}</h1>
      <p className="lede">{t.demo.intro}</p>
      <p>
        <button type="button" onClick={run} disabled={running}>
          {running ? t.demo.running : t.demo.run}
        </button>
      </p>
      {error && (
        <p className="banner">
          {t.demo.failed} <span className="mono">{error}</span>
        </p>
      )}
      {result && <DemoResultCards result={result} />}
    </main>
  );
}
