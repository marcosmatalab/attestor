"""The layering contract, enforced rather than trusted.

Two invariants the README sells, walked out of the AST of every engine module so
they cannot quietly stop being true:

1. **No LLM, and no network, inside the engine.** The repository's headline is that
   the classification is a rule engine and that the whole suite runs with the wifi
   off. An import of an LLM SDK, an HTTP client or ``socket`` in an engine package
   would end both claims at once. Note what this means for RFC3161: the timestamp
   module is a pure codec precisely so that it passes this test.

2. **The engine never imports the API.** Dependencies point one way, so the engine
   stays usable as a library and testable without an HTTP client.

Checked with ``ast`` over the source, not by importing the modules: an import-time
check would only see what a particular run happened to execute.
"""

import ast
import pathlib

import pytest

ENGINE_PACKAGES = ("classifier", "annexiv", "ledger", "provenance", "governance")

SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "attestor"

# LLM SDKs: the decision must not be delegated to a model.
FORBIDDEN_LLM = {"openai", "anthropic", "langchain", "llama_index", "litellm", "transformers"}
# Network: the engine does no I/O over the wire, at all.
FORBIDDEN_NETWORK = {"httpx", "requests", "socket", "urllib", "urllib3", "aiohttp", "http"}
FORBIDDEN = FORBIDDEN_LLM | FORBIDDEN_NETWORK

ENGINE_MODULES = sorted(
    path for package in ENGINE_PACKAGES for path in (SRC / package).rglob("*.py")
)


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


@pytest.mark.parametrize("path", ENGINE_MODULES, ids=lambda p: p.name)
def test_engine_module_imports_no_llm_sdk_and_opens_no_socket(path: pathlib.Path) -> None:
    offending = imported_roots(path) & FORBIDDEN
    assert not offending, f"{path.relative_to(SRC)} imports {sorted(offending)}"


@pytest.mark.parametrize("path", ENGINE_MODULES, ids=lambda p: p.name)
def test_engine_module_does_not_import_the_api_layer(path: pathlib.Path) -> None:
    offending = {m for m in imported_modules(path) if m.startswith("attestor.api")}
    assert not offending, f"{path.relative_to(SRC)} imports {sorted(offending)}"


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

    assert imported_roots(offender) & FORBIDDEN == {"httpx", "openai"}
    assert {m for m in imported_modules(offender) if m.startswith("attestor.api")} == {
        "attestor.api.routes"
    }
