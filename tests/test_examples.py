"""Smoke tests for user-facing examples without device access."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import socket

import pytest


EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


def _example_paths() -> list[Path]:
    return sorted(EXAMPLES_DIR.glob("*.py"))


def test_examples_compile() -> None:
    """Every example remains syntactically valid."""

    paths = _example_paths()
    assert paths
    for path in paths:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")


@pytest.mark.parametrize("path", _example_paths(), ids=lambda path: path.stem)
def test_examples_import_without_network(monkeypatch: pytest.MonkeyPatch, path: Path) -> None:
    """Importing an example does not run its entry point or access a network."""

    def fail_network(*args: object, **kwargs: object) -> object:
        raise AssertionError("Example import attempted network access.")

    monkeypatch.setattr(socket, "create_connection", fail_network)
    module_name = f"example_smoke_{path.stem}"
    spec = spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.main)
