"use client";

import { useState } from "react";
import {
  api,
  type Classification,
  type Crosswalk,
  type Dossier,
  type Fria,
  type ProfileInput,
  type Timeline,
} from "@/lib/api";
import { AnnexIvCard } from "@/components/AnnexIvCard";
import { ClassificationCard } from "@/components/ClassificationCard";
import { CrosswalkCard } from "@/components/CrosswalkCard";
import { FriaCard } from "@/components/FriaCard";
import { QuestionnaireForm } from "@/components/QuestionnaireForm";
import { TimelineTable } from "@/components/TimelineTable";
import { useLocale } from "@/lib/i18n/LocaleProvider";
import { Callout, Card, Skeleton } from "@/components/ui";
import sx from "@/components/sections.module.css";

interface Results {
  classification: Classification;
  timeline: Timeline;
  annexIv: Dossier | null;
  annexIvNote: string | null;
  crosswalk: Crosswalk;
  fria: Fria | null;
  friaNote: string | null;
}

export default function Home() {
  const { t } = useLocale();
  const [results, setResults] = useState<Results | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(profile: ProfileInput) {
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const [classification, timeline, crosswalk] = await Promise.all([
        api.classify(profile),
        api.timeline(profile),
        api.crosswalk(profile),
      ]);
      // Annex IV and FRIA are gated by the engine; a 422 means "does not apply" — surface the
      // engine's own message rather than hiding the section.
      // The gated note is the engine's real message (verbatim); on a non-Error fall back to
      // null so the card shows its own translated "not applicable" instead of fixed English.
      let annexIv: Dossier | null = null;
      let annexIvNote: string | null = null;
      try {
        annexIv = await api.annexIv(profile);
      } catch (x) {
        annexIvNote = x instanceof Error ? x.message : null;
      }
      let fria: Fria | null = null;
      let friaNote: string | null = null;
      try {
        fria = await api.fria(profile);
      } catch (x) {
        friaNote = x instanceof Error ? x.message : null;
      }
      setResults({ classification, timeline, annexIv, annexIvNote, crosswalk, fria, friaNote });
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.requestFailed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1 className={sx.title}>{t("classify.title")}</h1>
      <p className={sx.lead}>{t("classify.lead")}</p>

      <QuestionnaireForm onSubmit={run} busy={loading} />

      <div className={sx.results} aria-live="polite" aria-busy={loading}>
        {error && (
          <Callout tone="error" role="alert">
            {error}
          </Callout>
        )}
        {loading && (
          <Card title={t("common.working")}>
            <Skeleton lines={4} />
          </Card>
        )}
        {!loading && !error && !results && (
          <Callout tone="muted">{t("classify.emptyHint")}</Callout>
        )}
        {!loading && results && (
          <>
            <ClassificationCard c={results.classification} />
            <TimelineTable timeline={results.timeline} />
            <AnnexIvCard dossier={results.annexIv} note={results.annexIvNote} />
            <CrosswalkCard crosswalk={results.crosswalk} />
            <FriaCard fria={results.fria} note={results.friaNote} />
          </>
        )}
      </div>
    </>
  );
}
