"""C2PA content provenance: sign AI outputs with verifiable Content Credentials.

F4 covers SIGNING only (verification and the trust nuance are F5). Signing serves
the Art. 50 transparency obligation by marking AI-generated content, but C2PA is a
provenance/integrity signal, not proof of truth — see the README honesty note.
"""

from attestor.provenance.devcert import generate_dev_cert

__all__ = [
    "generate_dev_cert",
]
