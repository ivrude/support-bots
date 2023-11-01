from aiogram import Bot, Dispatcher


from .settings.configs import TOKEN

bot = Bot(token=TOKEN)



dp = Dispatcher(bot,)
Bot.set_current(bot)
