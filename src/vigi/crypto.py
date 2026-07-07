"""Cryptographic helpers for documented OpenAPI authentication."""

from __future__ import annotations

import hashlib

from vigi.exceptions import AuthenticationError


def sha256_hex(value: str) -> str:
    """Return a SHA-256 hex digest for OpenAPI Digest authentication inputs."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def calculate_digest_response(
    *,
    username: str,
    password: str,
    realm: str,
    nonce: str,
    method: str,
    uri: str,
    algorithm: str = "SHA-256",
) -> str:
    """Calculate the response field for the documented VIGI Digest flow."""

    if algorithm.upper() != "SHA-256":
        raise AuthenticationError(f"Unsupported digest algorithm: {algorithm}")

    ha1 = sha256_hex(f"{username}:{realm}:{password}")
    ha2 = sha256_hex(f"{method.upper()}:{uri}")
    return sha256_hex(f"{ha1}:{nonce}:{ha2}")
