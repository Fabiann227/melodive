import aiosqlite
from database import DB_PATH

async def load_banned_words() -> list[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT word FROM banned_words")
        return [row[0].lower() for row in await cur.fetchall()]