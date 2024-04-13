from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


# @router.message()
# async def echo(message: Message):
#     await message.answer(message.text)
#

@router.message(Command('start'))
async def start_command(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name},'
                        f' ты попал в бота, интрегрированного с системой управления проектами')
