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


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


async def main_bot():
    token = os.getenv("BOT_TOKEN")
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main_bot())