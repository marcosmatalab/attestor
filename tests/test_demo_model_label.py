"""The demo's AI-disclosure label must not name a model this project does not use.

The C2PA manifest records which model produced an asset. The demo signs a synthetic
PNG that no model produced, so the label is a placeholder - and a placeholder that
names a real commercial model reads as a claim about how the output was made.
"""

import base64
import io
import json
import re
from pathlib import Path

import c2pa

from attestor.demo import run_demo

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = "example-model"

# Names of real model families; a placeholder must never look like one of these.
REAL_MODEL = re.compile(r"\b(claude|gpt|gemini|llama|mistral)-[\w.-]+", re.IGNORECASE)


def test_the_demo_labels_its_output_with_the_placeholder() -> None:
    signed = base64.b64decode(run_demo()["signed_asset_b64"])
    store = json.loads(c2pa.Reader("image/png", io.BytesIO(signed)).json())
    manifest = store["manifests"][store["active_manifest"]]
    disclosure = next(
        a["data"] for a in manifest["assertions"] if a["label"] == "com.attestor.ai_disclosure"
    )
    assert disclosure["model"] == PLACEHOLDER


def test_no_source_or_doc_names_a_real_model_as_the_producer() -> None:
    offenders = []
    for folder in ("src", "docs", "tests", "scripts"):
        for path in (ROOT / folder).rglob("*"):
            if path.suffix in {".py", ".md", ".yaml"} and path.is_file():
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if "model" in line and REAL_MODEL.search(line):
                        offenders.append(f"{path.relative_to(ROOT)}:{number}")
    assert not offenders, offenders
