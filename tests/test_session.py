from vigi import AuthMode
from vigi.session import SessionInfo


def test_session_info_bearer_headers_mask_repr() -> None:
    info = SessionInfo(
        authenticated=True,
        auth_mode=AuthMode.BEARER,
        token_type="bearer",
        expires_in=1800,
        access_token="access-token",
        refresh_token="refresh-token",
    )

    assert info.bearer_headers() == {"Authorization": "Bearer access-token"}
    assert "access-token" not in repr(info)
    assert "refresh-token" not in repr(info)
