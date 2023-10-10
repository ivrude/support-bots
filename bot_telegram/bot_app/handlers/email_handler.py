import requests
from aiogram import types
from email_validator import EmailNotValidError, validate_email

from .menu_handler import handle_settings_ua
from ..app import dp, storage
from ..settings.configs import (
    TOKEN_DOMAIN,
    headers,
    url_check_email,
    url_check_email_code,
    url_email_code,
)
from .utils import YourState, _


@dp.message_handler(
    lambda message: message.text == _("Email"),
    state=YourState.waiting_for_contact,
)
async def handle_email_choice(message: types.Message):
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]
    await YourState.waiting_for_email.set()
    await message.answer(
        _(
            "You have selected authorization by mail. Please enter your email.",
            locale=selected_language,
        )
    )


@dp.message_handler(lambda message: message.text, state=YourState.waiting_for_email)
async def handle_contact_email(message: types.Message):
    email = message.text
    data_to_store = {"email": email}
    await storage.update_data(
        chat=message.chat.id, user=message.from_user.id, data=data_to_store
    )
    try:
        validate_email(email)
        print("Email is valid")
    except EmailNotValidError as e:
        print(f"Email is not valid: {e}")
        await YourState.waiting_for_email.set()
        await message.answer(
            _("The email address you entered is incorrect. Please try again")
        )
        return
    print("33")
    params = {"email": email, "chat_id": message.chat.id}
    print("32")
    print(params)
    response = requests.get(url_check_email, headers=headers, params=params)
    print("31")
    result = response.json()
    print("30")
    print(result)
    if result["status"] == "error":
        await YourState.waiting_for_email.set()
        await message.answer(
            _(
                "This mail is not in the database. "
                "Make sure that you are logging in from the right account"
            )
        )
    else:
        stored_data = await storage.get_data(
            chat=message.chat.id, user=message.from_user.id
        )
        selected_language = stored_data["language"]
        params = {
            "email": email,
        }
        print(selected_language)
        headers_email = {
            "accept": "application/json",
            "DOMAIN-UUID": TOKEN_DOMAIN,
            "Content-Type": "application/json",
            "Accept-Language": selected_language,
        }

        response1 = requests.post(url_email_code, json=params, headers=headers_email)
        data = response1.json()
        print(data)
        dataResult = data["data"]["result"]
        if dataResult != "ok":
            await YourState.waiting_for_email.set()
            await message.answer(dataResult)
            return

        await YourState.waiting_for_code.set()

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("send code again")
        keyboard.add(button)
        await message.answer(
            _(
                "A verification code has been sent "
                "to your email address. Please enter it."
            ),
            reply_markup=keyboard,
        )


@dp.message_handler(
    lambda message: message.text == "send code again", state=YourState.waiting_for_code
)
async def again_code(message: types.Message):
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    email = stored_data["email"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(email)
    keyboard.add(button)
    await message.answer(
        "Click the email button or write your email", reply_markup=keyboard
    )
    await YourState.waiting_for_email.set()


@dp.message_handler(
    lambda message: message.text.isdigit(), state=YourState.waiting_for_code
)
async def handle_code(message: types.Message):
    code = message.text
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    email = stored_data["email"]
    params = {"email": email, "code": code}
    response = requests.get(url_check_email_code, headers=headers, params=params)
    code_data = response.json()

    if code_data["status"] == "error":
        await YourState.waiting_for_email.set()
        await message.answer(
            _(
                "Not right. Please make sure that you entered "
                "everything correctly and enter your email again"
            )
        )
        return

    buttons = [
        types.KeyboardButton(text=_("Menu")),
    ]

    keyboard = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(*buttons)

    await message.answer(_("Choose above"), reply_markup=keyboard)
    await YourState.main.set()
    await handle_settings_ua(message)