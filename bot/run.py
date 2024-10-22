import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from app.handlers import router
import os
from database.models import async_main


from app.commands import set_commands


admin_id = 1033911797
bot = Bot(token=os.getenv('TG_TOKEN'))
db = Dispatcher()


async def start_bot(bot: Bot):
    await bot.send_message(admin_id, text='Я запустился')


db.startup.register(start_bot)


async def main():
    await set_commands(bot)
    try:

        await async_main()
        db.include_router(router)
        await bot.delete_webhook(drop_pending_updates=True)
        await db.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('interrupted')
