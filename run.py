import asyncio
import logging

from aiogram import Bot, Dispatcher, F 
from config import TOKEN
from app.handlers import router


bot = Bot(token=TOKEN)
db = Dispatcher()


async def main():
    db.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await db.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('interrupted')