# A ledger you can verify, right now

Three files, all produced by `scripts/make_example_ledger.py` from the engine in this
repository:

- `records.json` — three append-only records: the classification, the Annex IV
  dossier, and the C2PA manifest, each anchored by SHA-256 digest only. The ledger
  stores *digests of* artifacts, never the artifacts.
- `signed_root.json` — the RFC 6962 Merkle root over those records, signed with
  Ed25519 (RFC 8032), together with the public key the signature was made with.
- `public_key.pem` — that same public key, published so a verifier can **pin** it.

The key's fingerprint (SHA-256 of the raw 32-byte key) is:

```
21ffc076b7eef2cce6884e0c6b382a9ad72e4ba3d4b7a971cc1f601a8bac5544
```

It is also printed in the release notes, so the pin does not rest on this folder alone.

## Verify it, with the signer pinned

No network and no private key:

```bash
attestor ledger verify examples/ledger --public-key examples/ledger/public_key.pem
# ledger VERIFIED (Merkle root intact, Ed25519 signature valid; signer pinned); no timestamp
#   signer_sha256 = 21ffc076…5544
# exit 0
```

Edit one byte and the verdict flips to **tampered**:

```bash
sed -i 's/sys-1/sys-9/' examples/ledger/records.json
attestor ledger verify examples/ledger --public-key examples/ledger/public_key.pem
# ledger TAMPERED - integrity_ok=False, signature_ok=True
# exit 1
git checkout examples/ledger/records.json
```

Edit a record **and re-seal it with a key of your own**, and the records and signature
agree with each other again. The pin is what catches it:

```bash
# ledger UNTRUSTED SIGNER - records intact and signed, but by a key other than the pinned one
# exit 3
```

## Why the pin matters

The signature is checked with the key stored in `signed_root.json`. On its own that
proves the records match *a* key, not *whose* key: anyone who edits the records can
re-seal them with a fresh one. `--public-key` names the key you expect, obtained from a
channel other than the folder you are checking. Without it, `attestor ledger verify`
still checks integrity and signature, exits `0` if they hold, and says
`signer not pinned` next to the fingerprint so you can compare it yourself.

**There is no private key here, and there never will be.** The Ed25519 key that
signed this root was generated into a temporary directory by
`scripts/make_example_ledger.py` and discarded with it. Re-running that script mints a
new key and a new `public_key.pem`; `tests/test_ledger_signer_pinning.py` then fails
until the fingerprint above is updated, so the two cannot drift apart silently.
