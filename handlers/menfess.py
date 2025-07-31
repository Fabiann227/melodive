from aiogram import Router, F,types
from config import CHANNEL_ID
from database import DB_PATH
from datetime import datetime
import aiosqlite

from utils.logger import setup_logger
logger = setup_logger("bot_logger", level="INFO")

router = Router()

@router.message(F.text, F.chat.type == "private")
async def handle_menfess(msg: types.Message):
    today = datetime.now().strftime("%Y-%m-%d")
    if not ((msg.text and msg.text.startswith("❤️‍🔥")) or (msg.caption and msg.caption.startswith("❤️‍🔥"))):
        return

    # ambil teks
    content_text = msg.text or msg.caption
    user_id = msg.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        # get or init user
        cur = await db.execute("SELECT daily_count, last_sent FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()

        if not row:
            await db.execute("INSERT INTO users (user_id, daily_count, last_sent) VALUES (?, ?, ?)", (user_id, 0, today))
            count = 0
        else:
            count, last_sent = row
            if last_sent != today:
                count = 0
                await db.execute("UPDATE users SET daily_count = 0, last_sent = ? WHERE user_id = ?", (today, user_id))

        if count >= 100:
            await msg.answer("⚠️ Kuota menfess hari ini sudah habis (100/100).")
            return

        # send to channel
        caption = f"{content_text}"

        try:
            if msg.photo:
                sent_msg = await msg.bot.send_photo(CHANNEL_ID, msg.photo[-1].file_id, caption=caption)
            elif msg.video:
                sent_msg = await msg.bot.send_video(CHANNEL_ID, msg.video.file_id, caption=caption)
            elif msg.voice:
                sent_msg = await msg.bot.send_voice(CHANNEL_ID, msg.voice.file_id, caption=caption)
            else:
                sent_msg = await msg.bot.send_message(CHANNEL_ID, caption)

            logger.info(f"Sent to channel ID: {sent_msg.chat.id}")

            await db.execute(
                "INSERT INTO menfess (user_id, channel_msg_id, date_sent) VALUES (?, ?, ?)",
                (user_id, sent_msg.message_id, today)
            )
            await db.execute("UPDATE users SET daily_count = daily_count + 1 WHERE user_id = ?", (user_id,))
            await db.commit()

            logger.info(f"Menfess sent by {user_id} as {sent_msg.message_id}")

            await msg.answer("✅ Pesan berhasil dikirim secara anonim.")

        except Exception as e:
            logger.error(f"Gagal kirim menfess: {e}")
            print(f"[ERROR] Gagal kirim menfess: {e}")
            await msg.answer("❌ Terjadi kesalahan saat mengirim menfess.")

async def contains_banned_words(text: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT word FROM banned_words")
        words = [row[0] for row in await cur.fetchall()]
        return any(w.lower() in text.lower() for w in words)