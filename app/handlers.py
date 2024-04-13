from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
router = Router()


# @router.message()
# async def echo(message: Message):
#     await message.answer(message.text)
#

@router.message(Command('start'))
async def start_command(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name},'
                         f' ты попал в бота, интрегрированного с системой управления проектами')


@router.message(Command('clear'))
async def clear_command(message: Message, bot: Bot):
    try:
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.chat.id, i)
    except TelegramBadRequest as ex:
        if ex.message == 'Bad Request: message to delete not found':
            print("Щеф, я все удалить!")
