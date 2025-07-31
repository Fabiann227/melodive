from aiogram import BaseMiddleware
from aiogram.types import Message
from utils.banned import load_banned_words

class BannedWordsMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        text = event.text or event.caption or ""
        text = text.lower()
        banned_words = await load_banned_words()
        if any(word in text for word in banned_words):
            await event.answer("❌ Pesan mengandung kata terlarang.")
            return
        return await handler(event, data)