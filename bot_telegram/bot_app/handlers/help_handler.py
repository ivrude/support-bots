from aiogram import types
from aiogram.dispatcher import FSMContext

from ..app import dp
from .utils import YourState, _


@dp.message_handler(lambda message: message.text == _("Help🧩"), state=YourState.main)
async def handle_help(message: types.Message, state: FSMContext):
    await message.answer("Help")
