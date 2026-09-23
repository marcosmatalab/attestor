# C2PA content provenance (F4, F5)

Signs an AI output with a C2PA manifest (Content Credentials) carrying an
AI-generated marking (`c2pa.actions.v2` + the IPTC `trainedAlgorithmicMedia`
source type) and an Attestor disclosure assertion. Built on `c2pa-python==0.36.0`.

```python
from attestor.provenance import ProvenanceMetadata, SignerConfig, generate_dev_cert, sign_asset

generate_dev_cert("dev_chain.pem", "dev_key.pem")  # dev only — never commit
config = SignerConfig(cert_path="dev_chain.pem", private_key_path="dev_key.pem")
sign_asset(
    "input.png",
    "signed.png",
    config,
    ProvenanceMetadata(title="input.png", model="example-model"),
)
```

- **Signing via `Signer.from_callback`** — the key signs inside a callback, which is
  the seam a KMS/HSM signer would plug into. Swapping the callback is the whole change
  such an integration would need; **no KMS backend ships here.** ES256 (EC P-256).
- **RFC3161 timestamp** is optional (`RFC3161_TSA_URL`): when set, the TSA
  countersignature gives the C2PA claim an AdES "T"-level trusted time, linking to
  the F6 ledger. Without it, signing is fully offline.
- **Keys are config-driven**, never hardcoded or committed. The dev certificate is
  a self-signed **leaf + Root CA chain** (c2pa-rs rejects a lone self-signed cert).

### What C2PA proves, and what this is not (honesty)

- **C2PA proves PROVENANCE and INTEGRITY, not truth.** A valid Content Credential
  shows the manifest is intact and identifies the signer — it does **not** assert
  the content is real. **Absence** of a credential does **not** mean AI-generated;
  **presence** does not mean the content is authentic.
- **C2PA does not require declaring AI origin.** A validly signed asset may omit the
  `digitalSourceType` entirely. Attestor *chooses* to include the disclosure (in
  service of **Art. 50** of Reg. (EU) 2024/1689) — its presence is Attestor's choice,
  not something C2PA imposes.
- **The dev signer is an untrusted, self-signed certificate** — **not** on any C2PA
  trust list. A verifier marks the signer as untrusted; that trust nuance (and the
  verifier itself) is **F5**, below.

---

## C2PA content provenance — verifier (F5)

Reads a (possibly signed) asset and reports its provenance as **two independent
dimensions** — integrity and signer trust — that must never be conflated. Built on
the same `c2pa-python==0.36.0`.

```python
from attestor.provenance import verify_asset

report = verify_asset("signed.png")
report.validation_state  # "Valid" — manifest intact, claim well-formed
report.integrity_ok  # True
report.trusted  # False — the signer is NOT on any trust list
report.trust_reason  # "signingCredential.untrusted: ... not on any configured trust list"
report.headline  # "integrity Valid (...); signer UNTRUSTED — ..."
```

- **Integrity** (`validation_state`) answers "is the manifest intact and the claim
  well-formed?" — verified by the C2PA hashes and the claim signature.
- **Trust** (`trusted` / `trust_reason`) answers, **separately**, "is the *signer*
  recognised?" — derived from the `signingCredential.*` validation code, fail-closed
  (untrusted unless a trust anchor is configured and the chain validates against it).
- Verification is **deterministic**: identical bytes always produce an identical
  report (the report keeps validation **codes** but not the per-signature URN urls).
- An **unsigned** asset yields `has_manifest=False` without raising; **tampering** with
  a signed asset flips `validation_state` to `"Invalid"`.

### Why "Valid" is not "trusted" (honesty)

- **`validation_state == "Valid"` means the manifest is intact and the claim is
  well-formed — it does NOT mean the signer is trusted.** These are different
  questions with different answers.
- The proof is concrete: Attestor's dev-signed asset is `"Valid"` **and** carries a
  `signingCredential.untrusted` entry in the validation *failure* list **at the same
  time**. Attestor reports both, and the `headline` never states "Valid" on its own.
- **The dev signer is untrusted** because its CA is on no C2PA trust list. A real
  deployment signs with a certificate from a **recognised CA** and configures the
  verifier's trust anchors — at which point the same code reports `trusted=True`.
  Configuring the trust list is a deployment concern; F5 ships none.
- **Absence** of a credential does not mean content is non-AI; **presence** of a valid
  credential does not make the source trusted; and the **AI disclosure is voluntary**
  (C2PA does not require it).
