from aiogram import types
from aiogram.dispatcher import FSMContext

from ..app import dp
from .utils import _


@dp.message_handler(commands=["start"])
async def handle_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton("English🏴󠁧󠁢󠁥󠁮󠁧󠁿", callback_data="lang_en"))
    keyboard.add(types.InlineKeyboardButton("Українська🇺🇦", callback_data="lang_uk"))
    keyboard.add(types.InlineKeyboardButton("Руский🏳‍🌈", callback_data="lang_ru"))

    await message.answer("Сhoose language:", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == _("Back"), state="*")
async def handle_back(message: types.Message, state: FSMContext):
    await state.finish()
    await handle_start(message)
