from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='инициализация запуска бота'
        ),
        BotCommand(
            command='help',
            description='Помощь в работе с ботом'
         ),
        BotCommand(
            command='create_task',
            description='Создание задачи'
        ),
        BotCommand(
            command='delete_task',
            description='удаление задачи'
        ),
        BotCommand(
            command='get_data',
            description='Получение отчета по пользователю'
        ),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
