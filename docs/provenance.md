# C2PA provenance (F4, F5)

Attestor signs an AI output with a C2PA Content Credential and verifies it again.
The credential carries the classification that produced the output, so a verifier
holding only the signed asset can recover the checksum and re-run the decision.

## Signing (F4)

```python
from attestor import __version__
from attestor.classifier import SystemProfile, classify, load_bundle
from attestor.provenance import (
    build_manifest,
    build_signer,
    sign_bytes,
    signing_material_from_settings,
    synthetic_png,
)

bundle = load_bundle()
profile = SystemProfile(role="provider", annex_iii_area="employment")
classification = classify(profile, bundle)

manifest = build_manifest(classification, title="output.png", version=__version__)
signed = sign_bytes(manifest, synthetic_png(), build_signer(signing_material_from_settings()))
```

The manifest is **derived, not written**: the `eu.attestor.classification` assertion
carries the risk tier, the bundle version and hash, the classification checksum and
every obligation with its effective date. Nothing in it is prose.

### The signing seam

`build_signer` uses `Signer.from_callback`, so the private key is reached through a
single `bytes -> bytes` function rather than handed to the C2PA library:

```python
def sign_callback(data: bytes) -> bytes:
    return private_key.sign(data, ec.ECDSA(hashes.SHA256()))
```

That function is the seam a KMS or HSM signer plugs into: replace its body with a
call to `kms.sign` and nothing else in the module changes. **No KMS backend is
implemented here.** `signing_material_from_settings()` reads `C2PA_CERT_PATH` and
`C2PA_PRIVATE_KEY_PATH` when both are set, and otherwise mints an ephemeral
development chain, which is why the repository signs with no keys and no network.

### Two certificate requirements that are easy to miss

The C2PA certificate profile is narrow. Both of these cost a bare
`Signature: the certificate is invalid` at signing time, with no further detail:

- the end-entity certificate needs an extended key usage of `emailProtection` or
  `documentSigning`;
- it needs subject and authority key identifiers.

Similarly, a `c2pa.created` action without a `digitalSourceType` is reported as
`assertion.action.malformed` and invalidates the whole manifest.

## Verification (F5), and the distinction that matters

A Content Credential can be perfectly intact and signed by someone nobody
recognises. Those are **two different facts**, and collapsing them into one verdict
is how provenance tooling misleads people:

- report "invalid" for an unrecognised signer, and an intact file looks tampered;
- report "valid", and an unknown signer looks endorsed.

So `ProvenanceReport` carries them separately, and the headline always states both:

```text
integrity Valid (manifest intact, claim well-formed); signer UNTRUSTED (not in a recognised C2PA trust list)
```

| Field | Meaning |
|---|---|
| `validation_state` | C2PA's own state for the manifest |
| `integrity_ok` | no failure codes other than trust-related ones |
| `trusted` | the signer resolved against a trust list |
| `integrity_failures` / `trust_failures` | the raw codes, split along the same line |
| `classification_checksum` | recovered from the assertion, so the decision can be re-run |

With the development certificates this repository ships, the honest answer is
*integrity Valid, signer UNTRUSTED*, and that is exactly what `attestor demo`
prints. It is not a defect to be explained away; it is the correct report for a
self-signed chain.

## What this does not prove

A valid credential shows the manifest is intact and says who signed it. It does
**not** assert the content is accurate. And the **absence** of a credential does not
mean content was AI-generated.
