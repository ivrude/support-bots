from aiogram import Bot, types,Dispatcher

from aiohttp import web

from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN =("6059087374:AAEg4bLEIJqF-PFkjwfIDeOSbESRrJsvvLs")
bot = Bot(token=TOKEN)

storage = MemoryStorage()
dp=Dispatcher(bot, storage=storage)
app=web.Application()
webhook_path=f'/{TOKEN}'
Bot.set_current(bot)