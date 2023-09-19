from aiogram import types

from ..app import dp
from .utils import YourState, _


@dp.message_handler(lambda message: message.text == _("Settings"), state=YourState.main)
async def handle_settings_user(message: types.Message):  # noqa

    button1 = types.KeyboardButton(_("Profile"))
    button2 = types.KeyboardButton(_("Notifications"))
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(button1)
    keyboard.add(button2)
    await message.answer(_("Choose above"), reply_markup=keyboard)
    await YourState.settings.set()


@dp.message_handler(
    lambda message: message.text == _("Notifications"),
    state=YourState.settings,
)
async def handle_notifications_eng(message: types.Message):

    button1 = types.KeyboardButton(_("Get Notifications"))
    button2 = types.KeyboardButton(_("Dont get Notifications"))
    button3 = types.KeyboardButton(_("Menu"))
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    await message.answer(_("Choose above"), reply_markup=keyboard)

    await YourState.main.set()
