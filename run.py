import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from app.handlers import router
import os
from dotenv import load_dotenv



load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
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