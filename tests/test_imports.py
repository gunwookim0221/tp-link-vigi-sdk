import importlib


def test_public_modules_import() -> None:
    modules = [
        "vigi",
        "vigi.client",
        "vigi.auth",
        "vigi.capabilities",
        "vigi.devices",
        "vigi.records",
        "vigi.stream",
        "vigi.exceptions",
    ]

    for module_name in modules:
        assert importlib.import_module(module_name)
