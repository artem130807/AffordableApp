import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.domain.entities import Permission
from app.infrastructure.orm.models import Base
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def test_unit_of_work_commits_and_rolls_back_as_one_transaction() -> None:
    asyncio.run(_verify_transaction_boundary())


async def _verify_transaction_boundary() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    committed = Permission(code="test.committed", name="Committed")
    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        await unit_of_work.permissions.add(committed)
        await unit_of_work.commit()

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        stored = await unit_of_work.permissions.get_by_code(committed.code)
        assert stored is not None
        assert stored.id == committed.id

    rolled_back = Permission(code="test.rolled_back", name="Rolled back")
    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        await unit_of_work.permissions.add(rolled_back)
        await unit_of_work.rollback()

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        assert await unit_of_work.permissions.get_by_code(rolled_back.code) is None

    automatically_rolled_back = Permission(code="test.exception", name="Exception")
    try:
        async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
            await unit_of_work.permissions.add(automatically_rolled_back)
            raise RuntimeError("force rollback")
    except RuntimeError:
        pass

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        assert await unit_of_work.permissions.get_by_code(automatically_rolled_back.code) is None

    await engine.dispose()
