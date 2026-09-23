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
# Offline verifier — public artifacts only (records.json, signed_root.json, optional tsa/*.pem)
attestor ledger verify examples/ledger
# ledger VERIFIED (Merkle root intact, Ed25519 signature valid); no timestamp
# exit 0

# Edit one byte and the verdict flips, while the signature still checks out
sed -i 's/sys-1/sys-9/' examples/ledger/records.json
attestor ledger verify examples/ledger
# ledger TAMPERED - integrity_ok=False, signature_ok=True
# exit 1
git checkout examples/ledger/records.json
```

`python -m attestor.ledger <dir>` is the same verifier without installing the
package. Exit codes are the interface: `0` verified, `1` tampered, `2` usage or I/O
error — and TSA trust never moves them.

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
