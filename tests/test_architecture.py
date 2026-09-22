"""The layering contract, enforced rather than trusted.

Three invariants the README sells, walked out of the AST of every engine module so
they cannot quietly stop being true:

1. **No LLM touches the decision.** The repository's headline is that the
   classification is a rule engine. An LLM SDK imported anywhere in the engine would
   end that claim, so this one is absolute.

2. **The engine never imports the API.** Dependencies point one way, so the engine
   stays usable as a library and testable without an HTTP client.

3. **Network access is confined to one named module.** This is the honest version of
   "offline". The engine is not network-free: ``ledger/timestamp.py`` fetches an
   RFC 3161 token over HTTP, because obtaining a trusted timestamp inherently needs a
   TSA. What matters is that the boundary is narrow and checkable: that is the *only*
   module in the whole engine allowed to import a network client, the call is opt-in
   (it runs only when ``RFC3161_TSA_URL`` is configured), and **no verifier anywhere
   imports one**. Verifying a ledger, a C2PA credential or a classification needs no
   network, which is what the README actually promises.

Checked with ``ast`` over the source rather than by importing: an import-time check
would only see what a particular run happened to execute.
"""

import ast
import pathlib

import pytest

ENGINE_PACKAGES = ("classifier", "annexiv", "ledger", "provenance", "governance")

SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "attestor"

# LLM SDKs: the decision must never be delegated to a model.
FORBIDDEN_LLM = frozenset(
    {"openai", "anthropic", "langchain", "llama_index", "litellm", "transformers", "ollama"}
)

# Network clients. Allowed in exactly one module, listed below.
NETWORK_MODULES = frozenset(
    {"httpx", "requests", "socket", "urllib", "urllib3", "aiohttp", "http", "websockets"}
)

# The single sanctioned network seam: requesting an RFC 3161 token from a TSA.
NETWORK_ALLOWED = frozenset({"ledger/timestamp.py"})

ENGINE_MODULES = sorted(
    path for package in ENGINE_PACKAGES for path in (SRC / package).rglob("*.py")
)


def _relative(path: pathlib.Path) -> str:
    return path.relative_to(SRC).as_posix()


def imported_roots(path: pathlib.Path) -> set[str]:
    """Every top-level module name imported by ``path``."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def imported_modules(path: pathlib.Path) -> set[str]:
    """Every imported module, with its dotted path intact."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module)
    return modules


def test_the_engine_packages_were_actually_found() -> None:
    """Guards against the whole contract passing because it scanned nothing."""
    assert len(ENGINE_MODULES) >= 15
    for package in ENGINE_PACKAGES:
        assert (SRC / package).is_dir(), package


@pytest.mark.parametrize("path", ENGINE_MODULES, ids=_relative)
def test_engine_module_imports_no_llm_sdk(path: pathlib.Path) -> None:
    offending = imported_roots(path) & FORBIDDEN_LLM
    assert not offending, f"{_relative(path)} imports an LLM SDK: {sorted(offending)}"


@pytest.mark.parametrize("path", ENGINE_MODULES, ids=_relative)
def test_engine_module_does_not_import_the_api_layer(path: pathlib.Path) -> None:
    offending = {m for m in imported_modules(path) if m.startswith("attestor.api")}
    assert not offending, f"{_relative(path)} imports {sorted(offending)}"


@pytest.mark.parametrize("path", ENGINE_MODULES, ids=_relative)
def test_network_access_stays_inside_the_one_sanctioned_module(path: pathlib.Path) -> None:
    if _relative(path) in NETWORK_ALLOWED:
        return
    offending = imported_roots(path) & NETWORK_MODULES
    assert not offending, (
        f"{_relative(path)} imports a network client {sorted(offending)}. "
        f"Only {sorted(NETWORK_ALLOWED)} may, and only to request a timestamp."
    )


def test_the_sanctioned_seam_is_still_where_we_say_it_is() -> None:
    """If the TSA fetch moves or disappears, the allow-list is a lie and must change."""
    for allowed in NETWORK_ALLOWED:
        path = SRC / allowed
        assert path.is_file(), f"{allowed} is allow-listed but does not exist"
        assert imported_roots(path) & NETWORK_MODULES, (
            f"{allowed} no longer imports a network client; remove it from the allow-list"
        )


@pytest.mark.parametrize(
    "module",
    [
        "ledger/verifier.py",
        "provenance/verifier.py",
        "classifier/engine.py",
        "annexiv/citations.py",
    ],
)
def test_no_verifier_touches_the_network(module: str) -> None:
    """The promise a third party relies on: verifying needs nothing but the files."""
    path = SRC / module
    assert path.is_file(), module
    assert not imported_roots(path) & NETWORK_MODULES


def test_the_api_layer_is_allowed_to_depend_on_the_engine() -> None:
    """The arrow points one way; this asserts it points at all."""
    routes = imported_modules(SRC / "api" / "routes.py")
    assert any(module.startswith("attestor.classifier") for module in routes)


def test_the_contract_actually_catches_a_violation(tmp_path: pathlib.Path) -> None:
    """A gate nobody has seen fail is not a gate.

    Rather than describe the check, run it against a module that breaks it, so a
    refactor that silently neuters the walker fails here instead of going unnoticed.
    """
    offender = tmp_path / "engine_module.py"
    offender.write_text(
        "import httpx\nfrom openai import OpenAI\nfrom attestor.api.routes import router\n",
        encoding="utf-8",
    )

    assert imported_roots(offender) & FORBIDDEN_LLM == {"openai"}
    assert imported_roots(offender) & NETWORK_MODULES == {"httpx"}
    assert {m for m in imported_modules(offender) if m.startswith("attestor.api")} == {
        "attestor.api.routes"
    }
