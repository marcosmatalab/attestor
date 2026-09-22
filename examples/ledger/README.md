# A ledger you can verify, right now

Two files, both produced by the engine in this repository:

- `records.json` — three append-only records: the classification, the Annex IV
  dossier, and the C2PA manifest, each anchored by SHA-256 digest only. The
  ledger stores *digests of* artifacts, never the artifacts.
- `signed_root.json` — the RFC 6962 Merkle root over those records, signed with
  Ed25519 (RFC 8032), together with the public key needed to check it.

Verify it with no network, no keys and no trust in me:

```bash
attestor ledger verify examples/ledger
# ledger VERIFIED (Merkle root intact, Ed25519 signature valid); no timestamp
# exit 0
```

Then edit one byte and watch the verdict flip:

```bash
sed -i 's/sys-1/sys-9/' examples/ledger/records.json
attestor ledger verify examples/ledger
# ledger TAMPERED - integrity_ok=False, signature_ok=True
# exit 1
git checkout examples/ledger/records.json
```

That the signature still verifies while integrity fails is the point, not a
quirk: the signature covers the sealed root, so an edited record tells you *the
evidence was changed after sealing*, which is a different accusation from *the
signature is wrong*.

**There is no private key here, and there never will be.** The Ed25519 key that
signed this root was generated into a temporary directory by
`scripts/make_example_ledger.py` and discarded with it. Everything needed to
verify is public and is in `signed_root.json`. Re-running that script mints a new
key, so it produces a different — and equally valid — signature; these committed
files keep verifying regardless, and `tests/test_example_ledger.py` fails the
build if they ever stop.
