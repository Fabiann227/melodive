import aiosqlite

DB_PATH = "menfess.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            daily_count INTEGER DEFAULT 0,
            last_sent TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS menfess (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            channel_msg_id INTEGER,
            date_sent TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS banned_words (
            word TEXT PRIMARY KEY
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS reply_map (
            user_id INTEGER,
            private_msg_id INTEGER,
            channel_msg_id INTEGER,
            reply_to_msg_id INTEGER,
            PRIMARY KEY (user_id, private_msg_id)
        )""")
        await db.commit()
