from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyDatabaseHealth:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def is_ready(self) -> bool:
        try:
            await self.session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            await self.session.rollback()
            return False
        return True
