# The cryptographic ledger (F6)

An append-only list of records, sealed by an Ed25519 signature over an RFC 6962
Merkle root. Its promise is narrow, which is why it is keepable: *these artifacts
existed in exactly this form, in this order, before this root was sealed.*

The ledger stores **digests**, never the artifacts themselves.

## Verify it yourself

```bash
attestor ledger verify examples/ledger
# ledger VERIFIED (Merkle root intact, Ed25519 signature valid); no timestamp
#   integrity_ok = True
#   signature_ok = True
```

Exit codes are the interface: `0` verified, `1` tampered, `2` usage or I/O error.
Keeping "tampered" and "could not read it" apart matters, because a script that
treats a missing file as a passing ledger is worse than no check at all.

## Two axes, again

```bash
sed -i 's/sys-1/sys-9/' examples/ledger/records.json
attestor ledger verify examples/ledger
# ledger TAMPERED - integrity_ok=False, signature_ok=True
```

`integrity_ok` goes false while `signature_ok` stays true, because the signature
covers the sealed **root**, not the records. That combination tells an auditor *the
evidence was edited after sealing*, which is a different accusation from *the
signature is wrong* (which is what a rewritten root produces). Same principle as the
C2PA verifier: distinct failures must stay distinguishable.

## Why RFC 6962, and why Ed25519

**RFC 6962** for the domain-separation prefixes: a leaf is `SHA-256(0x00 || data)`
and an internal node is `SHA-256(0x01 || left || right)`. Without them an attacker
can present an internal node as a leaf, and "tamper-evident" stops being true. Odd
nodes are promoted unchanged rather than duplicated, which is the CVE-2012-2459 bug
in Bitcoin's variant; `tests/test_ledger_merkle.py` asserts that `[a,b,c]` and
`[a,b,c,c]` do not collide.

**Ed25519 (RFC 8032)** because its signatures are deterministic - no nonce, so the
same key over the same root always yields the same bytes - and because it has no
parameter choices to get wrong, which is the failure mode that actually bites in
ECDSA deployments.

## RFC3161 timestamps, and what is verified

`attestor.ledger.timestamp` is a **pure codec**: it builds a `TimeStampReq` and
parses a `TimeStampResp`, and it never opens a socket. That is deliberate, and it is
why the invariant "the engine does no network" is literally true and testable
(`tests/test_architecture.py`). Fetching the token over HTTP is the caller's job, at
the edge.

What **is** verified: that the token's `messageImprint` is the digest of the signed
root, i.e. that *this* token timestamps *this* ledger. That is the binding an
attacker would have to break to back-date evidence.

What is **not** verified, and is a documented simplification: the TSA's CMS
signature and its certificate chain. A full AdES "T" validation needs a CMS verifier
and a TSA trust list, neither of which ships here. So a token is reported as
*bound*, never as *trusted* - the same integrity/trust split the C2PA verifier uses,
for the same reason.

The fixture `tests/fixtures/ledger/timestamp.tsr` is a real response from a public
TSA, captured once. Testing the parser against a genuine token rather than one this
repository also wrote is the only way the test says anything: a round trip against
our own encoder would pass even if the encoder were wrong.

## Regenerating the example

```bash
python scripts/make_example_ledger.py
```

The Ed25519 private key is generated into a temporary directory and never written
into the repository, so re-running mints a new key and produces a different - and
equally valid - signature. The committed files keep verifying regardless, and
`tests/test_example_ledger.py` fails the build if they ever stop.
