"""Every tool `make check` invokes must be declared in the dev extra.

This is the phantom-dependency failure, caught twice already. `make check` shells
out to ruff, mypy, vulture and pytest by bare name, so on a developer machine they
resolve from whatever else is on PATH - another project's virtualenv, a global
install - and the gates pass. On a clean runner, where only `pip install -e
".[dev]"` has run, an undeclared tool is simply absent:

    mypy src/attestor
    make: mypy: No such file or directory
    make: *** [Makefile:23: typecheck] Error 127

So the Makefile is parsed rather than trusted: whatever `check` actually depends on
today is what must be declared, including gates added after this test was written.

Scope, stated plainly. This covers two things: the tools the `check` target
invokes, and the plugins implied by the flags pytest is given - on the `test`
recipe line or in `addopts` (a `--cov` flag needs pytest-cov, which the executable
name alone cannot reveal, because the tool is still `pytest`). It does not cover the
stub packages - types-PyYAML, types-reportlab - because nothing declares them
either; they are only felt when mypy runs, and a missing stub shows up as a mypy
error, not as exit 127.
"""

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"
PYPROJECT = ROOT / "pyproject.toml"


def normalize(name: str) -> str:
    """PEP 503 name normalisation, so types-PyYAML and types_pyyaml are one name."""
    return re.sub(r"[-_.]+", "-", name).lower()


def declared_dev_dependencies() -> set[str]:
    """The distribution names in [project.optional-dependencies].dev, without pins."""
    config = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    dev = config["project"]["optional-dependencies"]["dev"]
    return {normalize(re.split(r"[=<>!~\[;\s]", entry, maxsplit=1)[0]) for entry in dev}


def recipe_of(target: str) -> list[str]:
    """The tab-indented command lines belonging to a Makefile target."""
    lines = MAKEFILE.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if not line.startswith(f"{target}:"):
            continue
        commands = []
        for following in lines[index + 1 :]:
            if following.startswith("\t"):
                commands.append(following.lstrip("\t").strip())
            elif following.strip():
                break
        return commands
    raise AssertionError(f"the Makefile has no target named {target!r}")


def prerequisites_of(target: str) -> list[str]:
    """The targets `check` depends on, which is the gate list CI runs."""
    for line in MAKEFILE.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{target}:"):
            declaration = line.split(":", 1)[1].split("##", 1)[0]
            return declaration.split()
    raise AssertionError(f"the Makefile has no target named {target!r}")


def executable_of(command: str) -> str:
    """The tool a recipe line runs, seeing through `$(PYTHON) -m tool`."""
    tokens = command.split()
    if tokens[:2] == ["$(PYTHON)", "-m"] or tokens[1:2] == ["-m"]:
        return tokens[2]
    return tokens[0]


def tools_invoked_by_check() -> set[str]:
    tools = set()
    for gate in prerequisites_of("check"):
        commands = recipe_of(gate)
        assert commands, f"gate {gate!r} has no command, so the parse is wrong"
        tools.add(executable_of(commands[0]))
    return tools


def test_the_makefile_parse_actually_found_the_gates() -> None:
    """Without this, a parser that silently returns nothing would pass every test."""
    gates = prerequisites_of("check")
    assert len(gates) >= 4, f"only found {gates}, so `check` is not being read correctly"
    assert len(tools_invoked_by_check()) >= 4


def test_every_tool_make_check_runs_is_declared_in_the_dev_extra() -> None:
    declared = declared_dev_dependencies()
    missing = {tool for tool in tools_invoked_by_check() if normalize(tool) not in declared}

    assert not missing, (
        f"`make check` runs {sorted(missing)}, which no dev dependency installs. "
        "On a clean runner that is exit 127, not a test failure."
    )


def test_the_plugins_pytest_flags_imply_are_declared_too() -> None:
    """The tool is `pytest` either way; its flags are what make it need pytest-cov.

    The flags can come from two places, and both are read: the `test` recipe, where the
    coverage gate lives today, and addopts, where it lived before and could return.
    """
    config = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    addopts = config["tool"]["pytest"]["ini_options"]["addopts"]
    flags = " ".join([addopts, *recipe_of("test")])
    declared = declared_dev_dependencies()

    assert "--cov" in flags, "no --cov flag found, so this test would be checking nothing"
    assert "pytest-cov" in declared, "pytest is run with --cov, so pytest-cov must be installed"
