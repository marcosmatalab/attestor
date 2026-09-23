# Scope and boundaries

What Attestor is designed to do, and where its responsibility deliberately ends. Each module
doc has its own, more detailed section on the same subject; this page collects them.

## Legal notice

Attestor is a **portfolio project** built to demonstrate engineering across AI governance,
cryptography and compliance. It produces compliance *support and evidence* for human review;
it is **not legal advice**. The interpretation of the Regulation lives in a versioned bundle,
never hardcoded, so it can be reviewed and replaced.

## Boundaries by module

- **C2PA proves provenance, not truth.** A valid credential shows the manifest is intact and
  identifies the signer — **integrity is not trust**: a `"Valid"` state says nothing about
  whether the signer is recognised, and neither asserts the content is accurate. The
  **absence** of a credential does not mean content was AI-generated.
  See [`provenance.md`](provenance.md).
- **The ledger is an append-only log, not a blockchain.** It gives offline-verifiable
  integrity and existence proofs, but it is not distributed and has no consensus: the
  operator holds the key and can still rewrite history that is not yet signed and
  timestamped. See [`ledger.md`](ledger.md).
- **A pin is only as good as the channel it came from.** `attestor ledger verify
  --public-key` rejects a ledger sealed by any other key (`UNTRUSTED SIGNER`, exit 3). The
  pinned key has to reach the verifier by a channel the ledger's holder does not control;
  without a pin, the verdict is `SIGNER NOT PINNED` (exit 4), and `--allow-unpinned` is the
  explicit way to accept a ledger on consistency alone.
  See [`ledger.md`](ledger.md#pinning-the-signer).
- **Sealing a root may reach the network; verification never does.** An RFC 3161 timestamp
  has to be fetched from a timestamping authority. `tests/test_architecture.py` confines
  network imports to `ledger/timestamp.py` and asserts that no verifier imports a network
  client.
- **RFC 3161 tokens are checked; TSA trust is not granted.** No recognised-authority list
  ships, so a cryptographically valid token from a free TSA is reported untrusted. It never
  changes the tamper verdict or the exit code.
- **Governance artifacts help; they do not certify.** The ISO/IEC 42001 mapping is a
  reference crosswalk (IDs, no normative text), the FRIA is a scaffold for the deployer to
  complete, and the Art. 12 log is a capability — necessary, not sufficient, for conformity.
  See [`governance.md`](governance.md).
- **Annex IV citations are validated against the bundle, not against a lawyer.** See
  [`annex-iv.md`](annex-iv.md).
- **No KMS backend, and no database.** The signing seam (`Signer.from_callback`) exists; a
  KMS integration does not ship. Nothing in the engine persists state.
