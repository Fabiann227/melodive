from aiogram import Router, F,types
from config import CHANNEL_ID, DISCUSSION_ID
from database import DB_PATH
from datetime import datetime
import aiosqlite
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.logger import setup_logger
logger = setup_logger("bot_logger", level="INFO")

logger.info("Comment handler initialized.")

router = Router()

@router.message(F.reply_to_message)
async def handle_reply(msg: types.Message):
    logger.info(f"Received reply from {msg.from_user.id} in chat {msg.chat.id}")

    if msg.chat.id == DISCUSSION_ID:
        reply_to_msg = msg.reply_to_message

        # Ambil ID asli pesan channel, kalau tersedia
        channel_msg_id = getattr(reply_to_msg, "forward_from_message_id", None)

        if not channel_msg_id:
            logger.warning("forward_from_message_id tidak tersedia, fallback ke message_id (tidak direkomendasikan)")
            channel_msg_id = reply_to_msg.message_id

        logger.info(f"Replying to forwarded message ID: {channel_msg_id}")

        async with aiosqlite.connect(DB_PATH) as db:
            # Cari user dari tabel menfess berdasarkan channel_msg_id
            cur = await db.execute("SELECT user_id FROM menfess WHERE channel_msg_id = ?", (channel_msg_id,))
            row = await cur.fetchone()

            if row:
                # Reply ke menfess
                user_id = row[0]
                try:
                    channel_username = "ebhct"
                    comment_url = f"https://t.me/{channel_username}/{channel_msg_id}?comment={msg.message_id}"

                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="💬 Lihat Reply", url=comment_url)]
                    ])

                        
                    notif = await msg.bot.send_message(
                        chat_id=user_id,
                        text=f"💬 Kamu mendapat komentar anonim:\n\n\"{msg.text or '[non-text]'}\"\n\nBalas pesan ini untuk membalas secara anonim.",
                        reply_markup=keyboard
                    )
                    await db.execute("""
                        INSERT INTO reply_map (user_id, private_msg_id, channel_msg_id, reply_to_msg_id)
                        VALUES (?, ?, ?, ?)
                    """, (user_id, notif.message_id, msg.message_id, channel_msg_id))
                    await db.commit()
                    await msg.answer("✅ Komentar dikirim ke pengirim menfess secara anonim.")
                except Exception as e:
                    logger.error(f"Gagal kirim komentar ke user: {e}")
    else:
        # Kalau bukan reply ke menfess, coba cari di reply_map
        reply_to_msg = msg.reply_to_message
        user_id = msg.from_user.id
        reply_id = reply_to_msg.message_id
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("""
                SELECT channel_msg_id, reply_to_msg_id
                FROM reply_map
                WHERE user_id = ? AND private_msg_id = ?
            """, (user_id, reply_id))
            row = await cur.fetchone()

            if row:
                channel_msg_id, reply_to_msg_id = row
                try:
                    reply_text = f"💬 Balasan anonim:\n{msg.text or '[non-text]'}"

                    # Kirim sebagai reply ke komentar sebelumnya di grup diskusi
                    await msg.bot.send_message(
                        chat_id=DISCUSSION_ID,
                        text=reply_text,
                        reply_to_message_id=channel_msg_id  # reply ke komentar sebelumnya
                    )

                    await msg.answer("✅ Balasan anonim berhasil dikirim.")
                except Exception as e:
                    logger.error(f"Gagal kirim balasan: {e}")
                    await msg.answer("❌ Gagal mengirim balasan.")
