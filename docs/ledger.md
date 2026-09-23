# The cryptographic ledger (F6)

An **append-only log** of records (a dossier hash, a C2PA manifest hash, …). Each
record is hashed with the **same `canonical.py`** the classifier checksums with, the
leaves form a deterministic **RFC 6962 Merkle tree**, and the root is signed with
**Ed25519**. The signed root can optionally be **timestamped (RFC 3161)**. A third party
verifies everything **offline** — with only public artifacts, no private key and no
network.

```python
from attestor.ledger import Ledger, generate_ledger_key, load_private_key, save_ledger

generate_ledger_key("ledger.key")  # dev only — never commit; the path is config-driven
key = load_private_key("ledger.key")

ledger = Ledger()
ledger.append({"type": "dossier", "id": "sys-1", "sha256": "…"})
ledger.append({"type": "c2pa", "id": "img-1", "sha256": "…"})

signed = ledger.seal(key)  # Merkle root + Ed25519 signature (deterministic)
save_ledger("out/ledger", ledger.records, signed)
```

A ledger produced that way ships with the repository, so you can check the claim
before writing any of the above:

```bash
# Offline verifier — public artifacts only (records.json, signed_root.json, optional tsa/*.pem),
# with the signer pinned to the key the operator published
attestor ledger verify examples/ledger --public-key examples/ledger/public_key.pem
# ledger VERIFIED (Merkle root intact, Ed25519 signature valid; signer pinned); no timestamp
# exit 0

# Edit one byte and the verdict flips, while the signature still checks out
sed -i 's/sys-1/sys-9/' examples/ledger/records.json
attestor ledger verify examples/ledger --public-key examples/ledger/public_key.pem
# ledger TAMPERED - integrity_ok=False, signature_ok=True
# exit 1
git checkout examples/ledger/records.json
```

`python -m attestor.ledger <dir> (--public-key FILE | --allow-unpinned)` is the same
verifier without installing the package. Exit codes are the interface: `0` verified, `1`
tampered, `2` usage or I/O error, `3` untrusted signer, `4` signer not pinned — and TSA
trust never moves them.

### Pinning the signer

`signed_root.json` carries the public key its signature was made with, and the
signature is checked against that key. On its own that proves **consistency, not
identity**: whoever edits the records can re-seal them with a fresh key, and records,
root and signature agree again. `--public-key FILE` (PEM or 64 hex characters) names
the key the verifier expects. The verdicts, in order of precedence:

| Verdict | Meaning | Exit |
|---|---|:---:|
| `TAMPERED` | Records and signed root do not hold together | `1` |
| `UNTRUSTED SIGNER` | They hold together, but were sealed by a key other than the pinned one | `3` |
| `SIGNER NOT PINNED` | They hold together, but no `--public-key` was given, so who sealed them is unknown | `4` |
| `VERIFIED` | Intact and signed by the pinned key — or by any key, with `--allow-unpinned` | `0` |

The SHA-256 fingerprint of the signing key (`signer_sha256`) is printed on every run,
pinned or not. Passing both `--public-key` and `--allow-unpinned` is a usage error
(exit `2`). The same contract holds everywhere the ledger is verified: `verify_ledger()`
and `governance.verify_log()` take `expected_public_key` and `allow_unpinned`, the API's
`/api/ledger/verify` takes the same two fields and returns `signer_not_pinned` next to
`tampered` and `untrusted_signer`, and the demo pins the key it sealed with.

**Decision (0.3.0): without `--public-key`, the verdict is `SIGNER NOT PINNED`, exit
`4`.** In 0.2.0 a consistent ledger exited `0` without a pin, labelled
`signer not pinned` in the headline.

- *Why it changed:* a script reads the exit code, not the headline. An unpinned `0` let
  a ledger re-sealed by whoever edited it pass as a success to any caller that forgot
  the pin — the very attack the pin exists to stop. Now nobody gets a `0` without having
  named the signer, or having said explicitly that they do not care who it was.
- *Why `--allow-unpinned` exists:* "are these records intact, whoever signed them?" is a
  legitimate question — triage, or a ledger whose operator key is not at hand. It stays
  answerable, by name, with the previous behaviour: exit `0`, the `signer not pinned`
  label and the fingerprint to compare.
- *What it costs:* **the meaning of "no key" changed**, which breaks callers. A script
  that ran `attestor ledger verify DIR` and checked for `0` now gets `4` on a ledger it
  used to accept, and library code reading `verify_ledger(...).verified` without a key
  now reads `False`. That is a breaking change to the contract, so it ships as **0.3.0**
  (in 0.x, the MINOR number carries breaking changes). The fix for any caller is one
  argument: the operator's key, or `--allow-unpinned`.
- *Why `4` and not `3` or `1`:* each code names a different finding. `1` means the
  evidence changed after sealing; `3` means it was sealed by someone other than who you
  expected; `4` means you did not say who you expected. Tampering outranks both: an
  edited ledger is `1` with a pin or without one.

- **Deterministic.** Same records + same key → same Merkle root and same Ed25519
  signature (RFC 8032). The RFC 3161 token is *not* byte-reproducible (it depends on the
  TSA and the time), so it is verified, never byte-compared.
- **Inclusion proofs.** Given a record, the ledger emits an RFC 6962 audit path so a
  third party can verify membership **without** the whole tree.
- **Offline by construction.** Verification needs the public key, the signed root, the
  records (or an inclusion proof), and — for the timestamp — the TSA certificates. If it
  needed the private key or the network, the "offline" claim would be hollow.

### What the ledger proves, and what this is not (honesty)

- **It is an append-only log with cryptographic integrity — NOT a blockchain.** There is
  no distribution and no consensus; the operator holds the signing key. It gives
  third parties offline-verifiable integrity and existence evidence, nothing more.
- **The value, and its limit.** Once a root is **signed *and* timestamped**, altering
  the entries beneath it without detection is infeasible, and its existence at time *T*
  is demonstrable. **But** the operator can still fork or rewrite history that has **not
  yet been anchored** — the security depends on signing, timestamping, and ideally
  publishing roots **regularly**. Anchoring is a discipline, not a one-off.
- **Ed25519 ≠ legal identity.** The signature proves the root was signed by the holder
  of the key (authenticity and integrity of the root), not *who* in any legal sense.
- **RFC 3161 trust is a separate axis.** A timestamp proves existence-in-time **only by
  trusting the TSA**. A free/dev TSA can issue a perfectly valid token yet not be a
  recognised authority — so the verifier reports `tsa_trusted` **separately** and never
  lets an untrusted TSA look like a tampered ledger (the same integrity-vs-trust split as
  C2PA in F5). The exit code is driven by integrity and signature alone.
