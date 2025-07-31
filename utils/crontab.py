import aiocron
from database import DB_PATH
import aiosqlite
import logging

logger = logging.getLogger(__name__)

@aiocron.crontab('0 0 * * *')  # Jam 00:00
async def reset_daily_limit():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET daily_count = 0, last_sent = NULL")
        await db.commit()
        logger.info("🔄 Kuota harian semua user telah di-reset.")
