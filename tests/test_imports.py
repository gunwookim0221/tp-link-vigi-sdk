import importlib


def test_public_modules_import() -> None:
    modules = [
        "vigi",
        "vigi.client",
        "vigi.auth",
        "vigi.auth_provider",
        "vigi.capabilities",
        "vigi.crypto",
        "vigi.devices",
        "vigi.http_transport",
        "vigi.records",
        "vigi.session",
        "vigi.stream",
        "vigi.exceptions",
        "vigi.models",
        "vigi.transport",
        "vigi.types",
    ]

    for module_name in modules:
        assert importlib.import_module(module_name)
