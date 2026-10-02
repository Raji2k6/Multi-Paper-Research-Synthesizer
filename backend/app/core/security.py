import base64
import hashlib
import hmac
import json
import secrets
import time
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status

from app.core.config import settings


_PASSWORD_ITERATIONS = 600_000
_JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _PASSWORD_ITERATIONS,
    )
    return (
        f"pbkdf2_sha256${_PASSWORD_ITERATIONS}$"
        f"{_base64url_encode(salt)}${_base64url_encode(digest)}"
    )


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        algorithm, iterations, encoded_salt, encoded_digest = password_hash.split("$")
        iterations = int(iterations)
        if algorithm != "pbkdf2_sha256" or not 100_000 <= iterations <= 2_000_000:
            return False
        salt = _base64url_decode(encoded_salt)
        expected_digest = _base64url_decode(encoded_digest)
        candidate_digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(candidate_digest, expected_digest)


def create_access_token(subject: str) -> str:
    secret = _jwt_secret()
    issued_at = int(time.time())
    header = {"alg": _JWT_ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": subject,
        "iat": issued_at,
        "exp": issued_at + settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
    signing_input = (
        f"{_base64url_encode(json.dumps(header, separators=(',', ':')).encode())}."
        f"{_base64url_encode(json.dumps(payload, separators=(',', ':')).encode())}"
    )
    signature = hmac.new(
        secret.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_base64url_encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Your session is invalid or expired. Please sign in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        header_part, payload_part, signature_part = token.split(".")
        header = json.loads(_base64url_decode(header_part))
        payload = json.loads(_base64url_decode(payload_part))
        if not isinstance(header, dict) or not isinstance(payload, dict):
            raise unauthorized
        signing_input = f"{header_part}.{payload_part}"
        expected_signature = hmac.new(
            _jwt_secret().encode("utf-8"),
            signing_input.encode("ascii"),
            hashlib.sha256,
        ).digest()
        actual_signature = _base64url_decode(signature_part)
        if (
            header.get("alg") != _JWT_ALGORITHM
            or not hmac.compare_digest(actual_signature, expected_signature)
            or not isinstance(payload.get("sub"), str)
            or not payload["sub"]
            or not isinstance(payload.get("exp"), int)
            or payload["exp"] <= int(time.time())
        ):
            raise unauthorized
        return payload
    except HTTPException:
        raise
    except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
        raise unauthorized from None


def _jwt_secret() -> str:
    secret = settings.JWT_SECRET_KEY
    if not secret:
        secret_file = Path(__file__).resolve().parents[2] / ".jwt_secret"
        try:
            secret = secret_file.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            generated_secret = secrets.token_urlsafe(48)
            try:
                with secret_file.open("x", encoding="utf-8") as secret_stream:
                    secret_stream.write(generated_secret)
                secret = generated_secret
            except FileExistsError:
                secret = secret_file.read_text(encoding="utf-8").strip()
            except OSError as error:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=(
                        "Unable to create the local JWT signing key. Set "
                        "JWT_SECRET_KEY in backend/.env and restart the API."
                    ),
                ) from error
        except OSError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to read the local JWT signing key.",
            ) from error
    if len(secret) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "JWT_SECRET_KEY is not configured. Set a persistent, random "
                "secret of at least 32 characters in backend/.env."
            ),
        )
    return secret


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)
