import os

from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from dotenv import load_dotenv


load_dotenv()


url = os.getenv('DB_URL')

engine = create_async_engine(url)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    email: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column((String(100)))
    shtab_id: Mapped[int] = mapped_column()
    name: Mapped[str] = mapped_column(String(25))
    surname: Mapped[str] = mapped_column(String(25))
    role: Mapped[str] = mapped_column(String(25))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


