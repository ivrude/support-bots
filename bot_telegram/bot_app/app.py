from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiohttp import web

from .settings.configs import REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, TOKEN

bot = Bot(token=TOKEN)


storage = RedisStorage2(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    # и т.д.
)
dp = Dispatcher(bot, storage=storage)
app = web.Application()
webhook_path = f"/{TOKEN}"
Bot.set_current(bot)
