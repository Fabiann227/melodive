import asyncio
from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN
from database import init_db
from handlers import commands, menfess, comment
from middlewares.banned_filter import BannedWordsMiddleware
from utils import crontab
from aiogram.enums import ChatType
from keep_alive import keep_alive

from utils.logger import setup_logger
logger = setup_logger("bot_logger", level="INFO")

async def main():
    await init_db()

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.message.middleware(BannedWordsMiddleware())
    dp.include_router(comment.router)
    dp.include_router(commands.router)
    dp.include_router(menfess.router)

    logger.info("Bot started successfully.")

    await dp.start_polling(bot)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
