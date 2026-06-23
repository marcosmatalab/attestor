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

const ANNEX_III_AREAS = [
  "biometrics",
  "critical_infrastructure",
  "education",
  "employment",
  "essential_services",
  "credit_scoring",
  "life_health_insurance",
  "law_enforcement",
  "migration_border",
  "justice_democracy",
];

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
  const [role, setRole] = useState<"provider" | "deployer">("provider");
  const [area, setArea] = useState("employment");
  const [deployerType, setDeployerType] = useState("public_body");
  const [annexIEmbedded, setAnnexIEmbedded] = useState(false);
  const [isGpai, setIsGpai] = useState(false);
  const [interacts, setInteracts] = useState(false);
  const [synthetic, setSynthetic] = useState(false);
  const [results, setResults] = useState<Results | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function buildProfile(): ProfileInput {
    return {
      role,
      annex_iii_area: area === "none" ? null : area,
      deployer_type: role === "deployer" ? deployerType : null,
      annex_i_embedded: annexIEmbedded,
      is_gpai: isGpai,
      interacts_with_humans: interacts,
      generates_synthetic_content: synthetic,
      content_lifecycle: synthetic ? "new" : null,
    };
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);
    const profile = buildProfile();
    try {
      const [classification, timeline, crosswalk] = await Promise.all([
        api.classify(profile),
        api.timeline(profile),
        api.crosswalk(profile),
      ]);
      // Annex IV and FRIA are gated by the engine; a 422 means "does not apply" —
      // surface the engine's own message rather than hiding the section.
      let annexIv: Dossier | null = null;
      let annexIvNote: string | null = null;
      try {
        annexIv = await api.annexIv(profile);
      } catch (x) {
        annexIvNote = x instanceof Error ? x.message : "Not applicable.";
      }
      let fria: Fria | null = null;
      let friaNote: string | null = null;
      try {
        fria = await api.fria(profile);
      } catch (x) {
        friaNote = x instanceof Error ? x.message : "Not applicable.";
      }
      setResults({ classification, timeline, annexIv, annexIvNote, crosswalk, fria, friaNote });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h2>Classify an AI system</h2>
      <p className="lead">
        Answer the questionnaire; the deterministic engine resolves the risk tier, the applicable
        obligations and their effective dates, the Annex IV scaffold, and the governance artifacts.
      </p>

      <form className="card" onSubmit={onSubmit}>
        <div className="grid2">
          <div className="field">
            <label htmlFor="role">Operator role</label>
            <select
              id="role"
              value={role}
              onChange={(e) => setRole(e.target.value as "provider" | "deployer")}
            >
              <option value="provider">Provider</option>
              <option value="deployer">Deployer</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="area">Annex III high-risk area</label>
            <select id="area" value={area} onChange={(e) => setArea(e.target.value)}>
              <option value="none">none</option>
              {ANNEX_III_AREAS.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>
        </div>

        {role === "deployer" && (
          <div className="field">
            <label htmlFor="dt">Deployer type (relevant to the FRIA, Art. 27)</label>
            <select id="dt" value={deployerType} onChange={(e) => setDeployerType(e.target.value)}>
              <option value="public_body">public_body</option>
              <option value="private_public_service">private_public_service</option>
              <option value="other">other</option>
            </select>
          </div>
        )}

        <div className="checks">
          <label>
            <input
              type="checkbox"
              checked={annexIEmbedded}
              onChange={(e) => setAnnexIEmbedded(e.target.checked)}
            />
            Annex I embedded (product safety)
          </label>
          <label>
            <input type="checkbox" checked={isGpai} onChange={(e) => setIsGpai(e.target.checked)} />
            General-purpose AI (GPAI)
          </label>
          <label>
            <input
              type="checkbox"
              checked={interacts}
              onChange={(e) => setInteracts(e.target.checked)}
            />
            Interacts with humans (Art. 50(1))
          </label>
          <label>
            <input
              type="checkbox"
              checked={synthetic}
              onChange={(e) => setSynthetic(e.target.checked)}
            />
            Generates synthetic content (Art. 50(2))
          </label>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Classifying…" : "Classify"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}
      {results && <ResultsView r={results} />}
    </>
  );
}

function ResultsView({ r }: { r: Results }) {
  const c = r.classification;
  return (
    <>
      <div className="card">
        <h3>Classification</h3>
        <div style={{ marginBottom: 10 }}>
          <span className={`badge ${c.risk}`}>{c.risk}</span>
        </div>
        <div className="kv">
          <span className="k">Bundle</span>
          <span>
            {c.bundle_version} <span className="mono">({c.bundle_sha256.slice(0, 16)}…)</span>
          </span>
        </div>
        <div className="kv">
          <span className="k">Reproducible checksum</span>
          <span className="mono">{c.checksum}</span>
        </div>
        <table style={{ marginTop: 12 }}>
          <thead>
            <tr>
              <th>Obligation</th>
              <th>Reference</th>
              <th>Effective (legal text)</th>
            </tr>
          </thead>
          <tbody>
            {c.obligations.map((o) => (
              <tr key={o.id}>
                <td>{o.title}</td>
                <td className="mono">{o.reference}</td>
                <td>{o.effective_date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <TimelineView t={r.timeline} />
      <AnnexIvView dossier={r.annexIv} note={r.annexIvNote} />
      <CrosswalkView crosswalk={r.crosswalk} />
      <FriaView fria={r.fria} note={r.friaNote} />
    </>
  );
}

function TimelineView({ t }: { t: Timeline }) {
  return (
    <div className="card">
      <h3>Dual timeline — legal text vs Digital Omnibus</h3>
      <div className="caveat">
        The binding legal text remains Reg. (EU) 2024/1689. The Omnibus column is provisional:{" "}
        {t.omnibus_status || "pending formal adoption"}. Both dates are shown — never one as
        &quot;the&quot; date.
      </div>
      <table>
        <thead>
          <tr>
            <th>Obligation</th>
            <th>Legal text</th>
            <th>Omnibus (provisional)</th>
          </tr>
        </thead>
        <tbody>
          {t.obligations.map((o) => {
            const diverges = o.legal_text_date !== o.omnibus_date;
            return (
              <tr key={o.id}>
                <td>
                  <span className="mono">{o.reference}</span> {o.title}
                </td>
                <td>{o.legal_text_date ?? "—"}</td>
                <td className={diverges ? "diverges" : ""}>{o.omnibus_date ?? "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function AnnexIvView({ dossier, note }: { dossier: Dossier | null; note: string | null }) {
  if (!dossier) {
    return (
      <div className="card">
        <h3>Annex IV technical documentation</h3>
        <p className="muted">{note ?? "Not applicable to this classification."}</p>
      </div>
    );
  }
  return (
    <div className="card">
      <h3>Annex IV technical documentation</h3>
      <div className="note">
        &quot;Validated&quot; means each citation <strong>resolves and traces</strong> to an
        obligation the classifier emitted — not that it substantiates a claim. The sections are a
        scaffold to complete.
      </div>
      {dossier.sections.map((s) => (
        <div key={s.number} style={{ marginBottom: 10 }}>
          <strong>
            {s.number}. {s.title}
          </strong>
          {s.citations.length > 0 ? (
            <ul className="tight">
              {s.citations.map((cit) => (
                <li key={cit.obligation_id}>
                  <span className="mono">{cit.reference}</span> {cit.title} ({cit.effective_date})
                </li>
              ))}
            </ul>
          ) : (
            <div className="muted">No derived citations.</div>
          )}
        </div>
      ))}
    </div>
  );
}

function CrosswalkView({ crosswalk }: { crosswalk: Crosswalk }) {
  return (
    <div className="card">
      <h3>ISO/IEC 42001 crosswalk</h3>
      <div className="note">{crosswalk.disclaimer}</div>
      <table>
        <thead>
          <tr>
            <th>AI Act obligation</th>
            <th>Related ISO/IEC 42001 areas</th>
          </tr>
        </thead>
        <tbody>
          {crosswalk.entries.map((e) => (
            <tr key={e.obligation_id}>
              <td>
                <span className="mono">{e.reference}</span> {e.title}
              </td>
              <td>{e.iso_references.map((ref) => ref.label).join(", ")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function FriaView({ fria, note }: { fria: Fria | null; note: string | null }) {
  if (!fria) {
    return (
      <div className="card">
        <h3>FRIA — fundamental rights impact assessment (Art. 27)</h3>
        <p className="muted">{note ?? "Not applicable to this classification."}</p>
      </div>
    );
  }
  return (
    <div className="card">
      <h3>FRIA scaffold (Art. 27)</h3>
      <div className="muted" style={{ marginBottom: 8 }}>
        Trigger: {fria.trigger} · {fria.fria_reference}, effective {fria.fria_effective_date}
      </div>
      <div className="caveat">{fria.disclaimer}</div>
      <ul className="tight">
        {fria.sections.map((s) => (
          <li key={s.point}>
            <strong>({s.point})</strong> {s.requirement}
            <div className="muted mono">{s.placeholder}</div>
          </li>
        ))}
      </ul>
      <p className="muted">{fria.notify_authority_note}</p>
    </div>
  );
}
