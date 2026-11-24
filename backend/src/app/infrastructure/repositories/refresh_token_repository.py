from dataclasses import asdict
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import RefreshToken
from app.infrastructure.orm.models import RefreshTokenModel


def refresh_token_to_domain(model: RefreshTokenModel) -> RefreshToken:
    expires_at = model.expires_at
    created_at = model.created_at
    revoked_at = model.revoked_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)
    if revoked_at is not None and revoked_at.tzinfo is None:
        revoked_at = revoked_at.replace(tzinfo=UTC)
    return RefreshToken(
        id=model.id,
        user_id=model.user_id,
        token_hash=model.token_hash,
        expires_at=expires_at,
        created_at=created_at,
        revoked_at=revoked_at,
        replaced_by_token_id=model.replaced_by_token_id,
        user_agent=model.user_agent,
        ip_address=model.ip_address,
    )


class SqlAlchemyRefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, token: RefreshToken) -> RefreshToken:
        model = RefreshTokenModel(**asdict(token))
        self.session.add(model)
        await self.session.flush()
        return refresh_token_to_domain(model)

    async def get_by_hash(
        self,
        token_hash: str,
        *,
        for_update: bool = False,
    ) -> RefreshToken | None:
        query = select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        if for_update:
            query = query.with_for_update()
        model = await self.session.scalar(query)
        return refresh_token_to_domain(model) if model else None

    async def update(self, token: RefreshToken) -> RefreshToken:
        model = await self.session.get(RefreshTokenModel, token.id)
        if model is None:
            raise LookupError(token.id)
        model.revoked_at = token.revoked_at
        model.replaced_by_token_id = token.replaced_by_token_id
        await self.session.flush()
        return refresh_token_to_domain(model)

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        await self.session.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
