from database.models import async_session
from database.models import User
from sqlalchemy import select


async def set_user(tg_id, email, password, shtab_id, name, surname, role):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, email=email, password=password,
                             shtab_id=shtab_id, name=name, surname=surname, role=role))

            await session.commit()


async def check_user_in_BD(tg_id, email) -> bool:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        user2 = await session.scalar(select(User).where(User.email == email))
        return bool(user) and bool(user2)


async def shtab_id_by_tg_id(tg_id) -> int:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        return user.shtab_id


async def tg_id_by_stab_id(shtab_id) -> int:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.shtab_id == shtab_id))

        return user.tg_id


async def get_user_role(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user:
            return f'you role is  {user.role}'
        return 'access denied'


async def is_authorized(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return bool(user)


async def is_owner(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user.role == 'Owner':
            return True
        else:
            return False