import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt

from app.domain.exceptions import AuthenticationError
from app.infrastructure.config import Settings


class PasswordHasher:
    _n = 2**14
    _r = 8
    _p = 1
    _dummy_salt = b"affordable-dummy"
    _dummy_digest = hashlib.scrypt(
        b"not-a-real-password",
        salt=_dummy_salt,
        n=_n,
        r=_r,
        p=_p,
    )

    def hash(self, password: str) -> str:
        if not 8 <= len(password) <= 128:
            raise ValueError("Пароль должен содержать от 8 до 128 символов")
        salt = secrets.token_bytes(16)
        digest = hashlib.scrypt(
            password.encode(),
            salt=salt,
            n=self._n,
            r=self._r,
            p=self._p,
        )
        encoded_salt = base64.urlsafe_b64encode(salt).decode()
        encoded_digest = base64.urlsafe_b64encode(digest).decode()
        return f"scrypt${self._n}${self._r}${self._p}${encoded_salt}${encoded_digest}"

    def verify(self, password: str, encoded: str | None) -> bool:
        if encoded is None:
            digest = hashlib.scrypt(
                password.encode(),
                salt=self._dummy_salt,
                n=self._n,
                r=self._r,
                p=self._p,
            )
            hmac.compare_digest(digest, self._dummy_digest)
            return False
        try:
            algorithm, n, r, p, salt, expected = encoded.split("$")
            if algorithm != "scrypt" or (int(n), int(r), int(p)) != (
                self._n,
                self._r,
                self._p,
            ):
                return False
            digest = hashlib.scrypt(
                password.encode(),
                salt=base64.urlsafe_b64decode(salt),
                n=int(n),
                r=int(r),
                p=int(p),
            )
            return hmac.compare_digest(base64.urlsafe_b64encode(digest).decode(), expected)
        except (ValueError, TypeError):
            return False


class TokenService:
    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret
        self._issuer = settings.jwt_issuer
        self._audience = settings.jwt_audience
        self._access_ttl = timedelta(minutes=settings.access_token_ttl_minutes)
        self.refresh_ttl = timedelta(days=settings.refresh_token_ttl_days)

    def create_access_token(
        self,
        *,
        user_id: UUID,
        roles: list[str],
        permissions: frozenset[str],
    ) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id),
            "type": "access",
            "roles": roles,
            "permissions": sorted(permissions),
            "iat": now,
            "exp": now + self._access_ttl,
            "jti": str(uuid4()),
            "iss": self._issuer,
            "aud": self._audience,
        }
        return jwt.encode(payload, self._secret, algorithm="HS256")

    def decode_access_token(self, token: str) -> dict[str, object]:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                issuer=self._issuer,
                audience=self._audience,
                options={"require": ["exp", "iat", "sub", "type", "jti", "iss", "aud"]},
            )
        except jwt.PyJWTError as error:
            raise AuthenticationError("Недействительный или просроченный access-токен") from error
        if payload.get("type") != "access" or not payload.get("sub"):
            raise AuthenticationError("Неверный тип токена")
        return payload

    @staticmethod
    def create_refresh_token() -> tuple[str, str]:
        raw_token = secrets.token_urlsafe(48)
        return raw_token, TokenService.hash_refresh_token(raw_token)

    @staticmethod
    def hash_refresh_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()
