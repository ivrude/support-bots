
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from ..app import dp, bot
user_id = None
second_user_id = 5960202481
class YourState(StatesGroup):
    chat = State()

@dp.message_handler(lambda message:message.text not in ['/start', '/help'])
async def send_m(message: types.Message,state:FSMContext):
    print("11111111")
    if message.from_user.id == user_id:
        await bot.send_message(text=message.text, chat_id = second_user_id)
    elif message.from_user.id == second_user_id:
        await bot.send_message(text=message.text, chat_id = user_id)



@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message, state:FSMContext):
    global user_id
    user_id = message.from_user.id
    await message.reply("Соединение установлено! Теперь вы можете начать общение.")

