from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from core.config import settings


class PreBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)

engine = create_async_engine(settings.db_uri)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_session():
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
