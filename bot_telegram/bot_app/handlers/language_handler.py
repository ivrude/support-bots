from aiogram import types

from ..app import bot, dp, storage
from .utils import YourState, _


@dp.callback_query_handler(lambda query: query.data.startswith("lang_"))
async def language(callback_query: types.CallbackQuery):
    dataS = callback_query.data.split("_")
    selected_language = dataS[1]
    print(selected_language)

    user_id = callback_query.from_user.id

    data_to_store = {"language": selected_language}
    await storage.set_data(chat=user_id, user=user_id, data=data_to_store)

    await bot.send_message(
        user_id, _("Choosen language eanglish", locale=selected_language)
    )

    button1 = types.KeyboardButton(
        _("Phone number📞", locale=selected_language), request_contact=True
    )
    button2 = types.KeyboardButton(_("Email✉️", locale=selected_language))
    button3 = types.KeyboardButton(_("Back", locale=selected_language))
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    await bot.send_message(
        user_id,
        _("Choose how to auth", locale=selected_language),
        reply_markup=keyboard,
    )
    await YourState.waiting_for_contact.set()
