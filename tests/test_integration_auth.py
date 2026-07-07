import os

import pytest

from vigi import AuthConfig, AuthService, HttpTransport, TransportConfig


def _integration_config_available() -> bool:
    return all(
        os.getenv(name)
        for name in ("VIGI_HOST", "VIGI_USERNAME", "VIGI_PASSWORD")
    )


@pytest.mark.skipif(
    not _integration_config_available(),
    reason="VIGI auth integration environment is not configured.",
)
def test_integration_openapi_authentication() -> None:
    verify_ssl = os.getenv("VIGI_VERIFY_SSL", "true").lower() not in {"0", "false", "no"}
    config = AuthConfig(
        host=os.environ["VIGI_HOST"],
        username=os.environ["VIGI_USERNAME"],
        password=os.environ["VIGI_PASSWORD"],
        verify_tls=verify_ssl,
    )
    transport = HttpTransport(
        TransportConfig(
            base_url=f"https://{config.host}:{config.port}",
            verify_ssl=config.verify_tls,
        )
    )

    result = AuthService(config).authenticate(transport=transport)

    assert result.session_info.authenticated is True
    assert result.session_info.access_token
