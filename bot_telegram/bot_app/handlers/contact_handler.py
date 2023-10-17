import requests
from aiogram import types
from aiogram.dispatcher import FSMContext

from .menu_handler import handle_settings_ua
from ..app import dp, storage
from ..settings.configs import headers, url_check_number
from .utils import YourState, _


@dp.message_handler(
    lambda message: message.text == _("Phone number"),
    state=YourState.waiting_for_contact,
)
async def handle_phone_authorization(message: types.Message):
    await message.answer(
        _("Authorization by phone. Please send your phone number."),
    )
    await YourState.waiting_for_contact.set()


@dp.message_handler(
    content_types=types.ContentTypes.CONTACT, state=YourState.waiting_for_contact
)
async def handle_contact_authorization(message: types.Message, state: FSMContext):
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(_("Back"))
    user_id = message.from_user.id
    if user_id != message.contact.user_id:
        await message.answer("not", reply_markup=keyboard)
        return
    else:
        contact = message.contact

        number = contact.phone_number
        if not number.startswith("+"):
            number = "+" + number
        params = {"number": number, "chat_id": message.chat.id}
        print(message.chat.id)
        print(message.from_user.id)
        print(params)
        response = requests.get(url_check_number, headers=headers, params=params)

        result = response.json()
        print(result)
        rez = result["status"]
        print(
            rez,
        )
        if rez == "error":
            await message.answer(
                _("This number is not in the database. Check the data carefully")
            )
            return

        await message.answer(
            _("You sucsesful autorised"), reply_markup=types.ReplyKeyboardRemove()
        )
        print(selected_language)

        await YourState.main.set()
        await handle_settings_ua(message)