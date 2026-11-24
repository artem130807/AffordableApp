from uuid import uuid4

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.domain.exceptions import AuthenticationError
from app.infrastructure.config import Settings
from app.infrastructure.security import PasswordHasher, TokenService


def _settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "APP_ENV": "test",
        "APP_DATABASE_URL": "sqlite+aiosqlite:///:memory:",
        "APP_JWT_SECRET": "a-secure-test-secret-with-32-characters",
    }
    values.update(overrides)
    return Settings.model_validate(values)


def test_password_hasher_rejects_tampered_cost_parameters() -> None:
    hasher = PasswordHasher()
    encoded = hasher.hash("strong-password")

    assert hasher.verify("strong-password", encoded)
    assert not hasher.verify("strong-password", encoded.replace("scrypt$16384", "scrypt$32768"))
    assert not hasher.verify("wrong-password", encoded)


@pytest.mark.parametrize(
    "encoded",
    ["", "not-a-hash", "scrypt$16384$8$1$invalid$invalid", "scrypt$x$8$1$a$b"],
)
def test_password_hasher_treats_malformed_database_values_as_invalid(encoded: str) -> None:
    assert not PasswordHasher().verify("strong-password", encoded)


def test_access_token_validates_audience_and_required_claims() -> None:
    service = TokenService(_settings(APP_JWT_AUDIENCE="web-client"))
    token = service.create_access_token(
        user_id=uuid4(),
        roles=["user"],
        permissions=frozenset(),
    )

    assert service.decode_access_token(token)["type"] == "access"
    with pytest.raises(AuthenticationError):
        TokenService(_settings(APP_JWT_AUDIENCE="another-client")).decode_access_token(token)


def test_production_rejects_development_secret() -> None:
    with pytest.raises(PydanticValidationError):
        _settings(
            APP_ENV="production",
            APP_DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
            APP_JWT_SECRET="development-secret-change-me-32-chars",
        )


def test_development_cors_defaults_support_localhost_and_loopback_ip() -> None:
    settings = _settings()

    assert "http://localhost:5173" in settings.cors_origins
    assert "http://127.0.0.1:5173" in settings.cors_origins
