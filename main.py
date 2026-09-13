import asyncio
import os
import threading
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from flask import Flask

from handlers import router

load_dotenv()

# сервак
app = Flask(__name__)
@app.route("/")
@app.route("/health")
def health():
    return "Bot is running", 200

dp = Dispatcher()
dp.include_router(router)


async def run_bot():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN не задан в Environment")
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


def start_bot_thread():
    asyncio.run(run_bot())


if __name__ == "__main__":
    # Запускаем бота в фоне
    threading.Thread(target=start_bot_thread, daemon=True).start()

    # Flask слушает порт, который даёт Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)