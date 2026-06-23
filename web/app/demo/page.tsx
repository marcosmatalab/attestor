"use client";

import { useState } from "react";
import { api, type DemoResult } from "@/lib/api";

export default function DemoPage() {
  const [result, setResult] = useState<DemoResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      setResult(await api.demo());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h2>End-to-end demo</h2>
      <p className="lead">
        One example path for a high-risk <strong>provider</strong>: classify → Annex IV → sign an AI
        output (C2PA) → verify → anchor in the ledger → verify the ledger offline. Every output below
        is produced live by the engine; signing and sealing use ephemeral dev keys generated per run.
      </p>

      <div className="card">
        <button onClick={run} disabled={loading}>
          {loading ? "Running the pipeline…" : "Run the demo"}
        </button>
      </div>

      {error && <div className="error">{error}</div>}
      {result && <DemoView result={result} />}
    </>
  );
}

function DemoView({ result }: { result: DemoResult }) {
  const prov = result.provenance;
  const ledger = result.ledger.verification;
  return (
    <>
      <div className="card">
        <h3>1 · Classification</h3>
        <div style={{ marginBottom: 8 }}>
          <span className={`badge ${result.classification.risk}`}>{result.classification.risk}</span>
        </div>
        <div className="kv">
          <span className="k">Checksum</span>
          <span className="mono">{result.classification.checksum}</span>
        </div>
        <div className="kv">
          <span className="k">Annex IV</span>
          <span>
            {result.annex_iv.system_name} — {result.annex_iv.sections.length} sections
          </span>
        </div>
      </div>

      <div className="card">
        <h3>2 · C2PA provenance</h3>
        <div style={{ marginBottom: 8 }}>
          <span className={`badge ${prov.trusted ? "ok" : "warn"}`}>
            {prov.trusted ? "signer trusted" : "signer untrusted"}
          </span>
        </div>
        <p className="mono">{prov.headline}</p>
        <div className="caveat">
          Integrity (<strong>{prov.validation_state}</strong>) means the manifest is intact — it does
          <strong> not</strong> mean the signer is trusted. The demo&apos;s dev certificate is on no
          C2PA trust list, so the signer is reported <strong>untrusted</strong>. &quot;Valid&quot; is
          never shown without the trust qualifier.
        </div>
        {prov.signer && (
          <div className="kv">
            <span className="k">Signer</span>
            <span>
              {prov.signer.common_name} · {prov.signer.algorithm}
            </span>
          </div>
        )}
        {prov.ai_disclosure && (
          <div className="kv">
            <span className="k">AI disclosure</span>
            <span className="mono">{prov.ai_disclosure.digital_source_type ?? "—"}</span>
          </div>
        )}
      </div>

      <div className="card">
        <h3>3 · Ledger (offline verification)</h3>
        <div style={{ marginBottom: 8 }}>
          <span className={`badge ${ledger.verified ? "ok" : "warn"}`}>
            {ledger.verified ? "verified" : "tampered"}
          </span>
        </div>
        <p className="mono">{ledger.headline}</p>
        <div className="kv">
          <span className="k">Merkle root</span>
          <span className="mono">{result.ledger.signed_root.merkle_root}</span>
        </div>
        <div className="kv">
          <span className="k">Anchored records</span>
          <span>{result.ledger.records.length}</span>
        </div>
        <div className="note">
          An append-only log with cryptographic integrity, verifiable offline by a third party —
          <strong> not a blockchain</strong> (no distribution, no consensus). The integrity and
          signature decide the verdict; TSA trust, when present, is reported separately.
        </div>
      </div>
    </>
  );
}
