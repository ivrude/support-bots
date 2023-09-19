from aiogram import types

from ..app import dp, storage
from .utils import YourState, _


@dp.message_handler(
    lambda message: message.text == _("Menu"),
    state=[
        YourState.waiting_for_wish,
        YourState.feedback,
        YourState.main,
        YourState.offers,
        YourState.settings,
        YourState.menu,
    ],
)
async def handle_settings_ua(message: types.Message):

    buttons = [
        types.KeyboardButton(text=_("News")),
        types.KeyboardButton(text=_("Settings")),
        types.KeyboardButton(text=_("Offers")),
        types.KeyboardButton(text=_("Help")),
        types.KeyboardButton(text=_("Support")),
    ]
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    print(stored_data)
    keyboard = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(*buttons)

    await message.answer(_("Choose menu punkt"), reply_markup=keyboard)
    await YourState.main.set()
