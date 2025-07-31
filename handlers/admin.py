from aiogram import Router, F
from aiogram.types import Message
from config import super_admin_id
from database import DB_PATH
import aiosqlite

from utils.logger import setup_logger, log, err
setup_logger()

router = Router()

log("Admin handler initialized.")

def is_super_admin(user_id: int) -> bool:
    return user_id == super_admin_id

async def is_admin(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
        return bool(await cur.fetchone())

@router.message(F.text.startswith("/setadmin"))
async def set_admin(msg: Message):
    if not is_super_admin(msg.from_user.id):
        return await msg.answer("❌ Hanya superadmin yang bisa menggunakan perintah ini.")

    try:
        uid = int(msg.text.split()[1])
    except:
        return await msg.answer("Gunakan format: /setadmin <user_id>")

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (uid,))
        await db.commit()
    await msg.answer(f"✅ User {uid} ditambahkan sebagai admin.")

@router.message(F.text.startswith("/addbanned"))
async def add_banned(msg: Message):
    if not await is_admin(msg.from_user.id):
        return

    try:
        word = msg.text.split()[1].lower()
    except:
        return await msg.answer("Gunakan format: /addbanned <kata>")

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO banned_words (word) VALUES (?)", (word,))
        await db.commit()
    await msg.answer(f"✅ Kata '{word}' ditambahkan ke daftar terlarang.")

@router.message(F.text.startswith("/delbanned"))
async def del_banned(msg: Message):
    if not await is_admin(msg.from_user.id):
        return

    try:
        word = msg.text.split()[1].lower()
    except:
        return await msg.answer("Gunakan format: /delbanned <kata>")

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM banned_words WHERE word = ?", (word,))
        await db.commit()
    await msg.answer(f"✅ Kata '{word}' dihapus dari daftar terlarang.")

@router.message(F.text == "/listbanned")
async def list_banned(msg: Message):
    # if not await is_admin(msg.from_user.id):
    #     return

    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT word FROM banned_words")
        words = [row[0] for row in await cur.fetchall()]
        await msg.answer("🚫 Banned Words:\n" + "\n".join(words))

