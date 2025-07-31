from aiogram import Router, F
from aiogram.types import Message
from database import DB_PATH
import aiosqlite
from datetime import datetime
from config import super_admin_id, DISCUSSION_ID

from utils.logger import setup_logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot
logger = setup_logger("bot_logger", level="INFO")

router = Router()

@router.message(F.text == "/start")
async def start_cmd(msg: Message, bot: Bot):
    try:
        member = await bot.get_chat_member(DISCUSSION_ID, msg.from_user.id)
        if member.status in ("left", "kicked"):
            raise Exception("Not a member")
    except Exception:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Join Group",
                        url="https://t.me/ebhctg"
                    )
                ]
            ]
        )
        return await msg.answer(
            "❗ Kamu harus join group utama dulu untuk menggunakan bot ini.",
            reply_markup=keyboard
        )
    await msg.answer(
        "👋 Selamat datang di Bot Menfess Anonim!\nGunakan /help untuk melihat panduan."
    )

@router.message(F.text == "/help")
async def help_cmd(msg: Message):
    desc = (
        "💡 Kirim menfess kamu dengan emoji ❤️‍🔥.\n"
        "Pastikan kamu sudah join group YAA!.\n\n"
        "Kategori:\n"
        "• #Mufriend - cari teman\n"
        "• #Murec - minta rekomendasi lagu\n"
        "• #Mupro - promosi lagu, baik idola atau lagu produksi sendiri (untuk musisi indie)\n"
        "• #Mustory - cerita yang berkaitan dengan lagu / musik\n"
        "• #Murandom - apapun tentang musik\n\n"
        "/kuota → Lihat sisa kuota menfess hari ini."
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Subscribe Channel 🎵",
                    url="https://t.me/musniverse"
                )
            ]
        ]
    )
    await msg.answer(desc, reply_markup=keyboard)

@router.message(F.text == "/kuota")
async def kuota_cmd(msg: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT daily_count, last_sent FROM users WHERE user_id = ?", (msg.from_user.id,))
        row = await cur.fetchone()
        today = datetime.now().strftime("%Y-%m-%d")
        if not row or row[1] != today:
            count = 0
        else:
            count = row[0]
        await msg.answer(f"📦 Kuota menfess hari ini: {100 - count}/100")

@router.message(F.text == "/dashboard")
async def dashboard(msg: Message):
    # if not await is_admin(msg.from_user.id):
    #     return

    logger.info(f"Dashboard requested by {msg.from_user.id}")

    async with aiosqlite.connect(DB_PATH) as db:
        u = await db.execute("SELECT COUNT(*) FROM users")
        m = await db.execute("SELECT COUNT(*) FROM menfess")
        user_count = (await u.fetchone())[0]
        menfess_count = (await m.fetchone())[0]

    await msg.answer(f"📊 Dashboard:\n👥 Pengguna: {user_count}\n📨 Total Menfess: {menfess_count}")

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
    if not await is_admin(msg.from_user.id):
        return

    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT word FROM banned_words")
        words = [row[0] for row in await cur.fetchall()]
        await msg.answer("🚫 Banned Words:\n" + "\n".join(words))