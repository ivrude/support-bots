from aiogram import types

from .menu_handler import handle_settings_ua
from ..app import dp, storage
from .utils import YourState, _


@dp.message_handler(lambda message: message.text == _("Settings⚙"), state=YourState.main)
async def handle_settings_user(message: types.Message):  # noqa
    button1 = types.KeyboardButton(_("Profile"))
    button2 = types.KeyboardButton(_("Notifications"))
    button3 = types.KeyboardButton(_("Language"))
    button4 = types.KeyboardButton(_("Menu"))
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    keyboard.add(button4)
    await message.answer(_("Choose above"), reply_markup=keyboard)
    await YourState.settings.set()


@dp.message_handler(
    lambda message: message.text == _("Language"), state=YourState.settings
)
async def handle_notifications(
    message: types.Message,
):
    button1 = types.KeyboardButton("Українська🇺🇦")
    button2 = types.KeyboardButton("Eanglish🏴󠁧󠁢󠁥󠁮󠁧󠁿")
    button3 = types.KeyboardButton("Руский🏳‍🌈")
    button4 = types.KeyboardButton(_("Menu"))
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    keyboard.add(button4)
    await message.answer(_("Choose above"), reply_markup=keyboard)

    await YourState.language.set()


@dp.message_handler(
    lambda message: message.text == "Українська🇺🇦", state=YourState.language
)
async def handle_notifications_uk(
    message: types.Message,
):
    selected_language = "uk"
    user_id = message.from_user.id

    data_to_store = {"language": selected_language}
    await storage.update_data(chat=user_id, user=user_id, data=data_to_store)
    await YourState.main.set()
    await handle_settings_ua(message)


@dp.message_handler(
    lambda message: message.text == "Eanglish🏴󠁧󠁢󠁥󠁮󠁧󠁿", state=YourState.language
)
async def handle_notifications_eng(
    message: types.Message,
):
    selected_language = "en"
    user_id = message.from_user.id

    data_to_store = {"language": selected_language}
    await storage.update_data(chat=user_id, user=user_id, data=data_to_store)
    await YourState.main.set()
    await handle_settings_ua(message)


@dp.message_handler(lambda message: message.text == "Руский🏳‍🌈", state=YourState.language)
async def handle_notifications_ru(
    message: types.Message,
):
    selected_language = "ru"
    user_id = message.from_user.id

    data_to_store = {"language": selected_language}
    await storage.update_data(chat=user_id, user=user_id, data=data_to_store)
    await YourState.main.set()
    await handle_settings_ua(message)


@dp.message_handler(
    lambda message: message.text == _("Notifications"),
    state=YourState.settings,
)
async def handle_notifications_user(message: types.Message):
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
