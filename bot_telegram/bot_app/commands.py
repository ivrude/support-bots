import asyncio

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import json
from email_validator import EmailNotValidError, validate_email

from .app import bot, dp, storage
from .settings.configs import (
    TOKEN_DOMAIN,
    headers,
    url_check_email,
    url_check_email_code,
    url_check_number,
    url_email_code,
    url_get_news,
    url_new_thread,
    url_news_list,
    TOKEN, url_send_photo, url_send_video
)
from .settings.locale import get_locale_middleware_sync, setup_locale_middleware


async def thread(chat_id, user_id):
    await asyncio.sleep(60)
    stored_data = await storage.get_data(chat=chat_id, user=user_id)
    print(stored_data)
    result = stored_data["thread"]["thread_result"]
    if not result:
        await YourState.main.set()
        await bot.send_message(
            chat_id=chat_id, text=_("Time is up, communication is complete")
        )
        data_to_store = {"thread": None}
        await storage.update_data(chat=chat_id, user=user_id, data=data_to_store)


setup_locale_middleware(dp)


class YourState(StatesGroup):
    waiting_for_contact = State()
    waiting_for_email = State()
    waiting_for_code = State()
    settings = State()
    menu = State()
    offers = State()
    main = State()
    feedback = State()
    waiting_for_feedback = State()
    waiting_for_complain = State()
    waiting_for_language = State()
    waiting_for_issue = State()
    chat = State()


i18n = get_locale_middleware_sync(dp)
_ = i18n.gettext

async def send_message_to_websocket(message, user_id, thread,token, photo=None):
    websocket_connection = dp.data['websocket_connection']

    data = {"message": message, "user_id": user_id, "thread": thread, "token":token}

    message_json = json.dumps(data)
    await websocket_connection.send(message_json)
@dp.message_handler(commands=["start"])
async def handle_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton("English", callback_data="lang_en"))
    keyboard.add(types.InlineKeyboardButton("Українська", callback_data="lang_uk"))
    keyboard.add(types.InlineKeyboardButton("Руский", callback_data="lang_ru"))

    await message.answer("Сhoose language:", reply_markup=keyboard)


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
        _("Phone number", locale=selected_language), request_contact=True
    )
    button2 = types.KeyboardButton(_("Email", locale=selected_language))
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


@dp.message_handler(lambda message: message.text == _("Back"), state="*")
async def handle_back(message: types.Message, state: FSMContext):
    await state.finish()
    await handle_start(message)


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

        buttons = [
            types.KeyboardButton(text=_("Menu")),
        ]

        keyboard = types.ReplyKeyboardMarkup(
            row_width=2, resize_keyboard=True, one_time_keyboard=True
        )
        keyboard.add(*buttons)

        await message.answer(_("Choose above"), reply_markup=keyboard)
        await YourState.main.set()


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


@dp.message_handler(
    lambda message: message.text == _("Menu"),
    state=[
        YourState.waiting_for_feedback,
        YourState.feedback,
        YourState.main,
        YourState.offers,
        YourState.settings,
        YourState.menu,
        YourState.chat,
    ],
)
async def handle_settings_ua(message: types.Message, state: FSMContext):

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


@dp.message_handler(lambda message: message.text == _("Settings"), state=YourState.main)
async def handle_settings_user(message: types.Message, state: FSMContext):  # noqa

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
async def handle_notifications_eng(message: types.Message, state: FSMContext):

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


@dp.message_handler(lambda message: message.text == _("News"), state=YourState.main)
async def handle_news(message: types.Message, state: FSMContext):

    await message.answer(_("This is list of our news"))

    response = requests.get(url_news_list, headers=headers)
    data = response.json()
    news_list = data["data"]["news"]
    print(data)
    print(news_list)
    i = 0
    if len(news_list) > 0:
        params = {"index": news_list[i]}
    else:
        await message.answer(_("This is empty"))
        return

    response_get = requests.get(url_get_news, headers=headers, params=params)
    data_news = response_get.json()
    print(data_news)
    dataResult = data_news["data"]["result"]

    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(types.InlineKeyboardButton(dataResult, callback_data="data_"))
    kb.add(
        types.InlineKeyboardButton("<<", callback_data=f"prev_{i}"),
        types.InlineKeyboardButton(">>", callback_data=f"next_{i}"),
    )

    chat_id = message.chat.id
    msg_id = message.message_id

    await bot.send_message(chat_id, _("Topik"), reply_markup=kb)

  
    await state.update_data(message_id=msg_id)
    await YourState.main.set()


@dp.callback_query_handler(
    lambda query: query.data.startswith("prev"), state=YourState.main
)
async def process_prev_button(callback_query: types.CallbackQuery, state: FSMContext):

    i = int(callback_query.data.split("_")[1]) - 1

    response = requests.get(url_news_list, headers=headers)
    data = response.json()
    news_list = data["data"]["news"]
    if i < 0:
        i = len(news_list) - 1
    if i >= len(news_list):
        i = 0

    print(data)
    print(news_list)
    params = {"index": news_list[i]}
    response_get = requests.get(url_get_news, headers=headers, params=params)
    data_news = response_get.json()
    print(data_news)
    dataResult = data_news["data"]["result"]

    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(types.InlineKeyboardButton(dataResult, callback_data="data_"))
    kb.add(
        types.InlineKeyboardButton("<<", callback_data=f"prev_{i}"),
        types.InlineKeyboardButton(">>", callback_data=f"next_{i}"),
    )

    user_id = callback_query.from_user.id
    await bot.edit_message_text(
        _("Topik"),
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        reply_markup=kb,
    )


@dp.callback_query_handler(
    lambda query: query.data.startswith("next"), state=YourState.main
)
async def process_next_button(callback_query: types.CallbackQuery, state: FSMContext):

    i = int(callback_query.data.split("_")[1]) + 1

    response = requests.get(url_news_list, headers=headers)
    data = response.json()
    news_list = data["data"]["news"]
    if i < 0:
        i = len(news_list) - 1
    if i >= len(news_list):
        i = 0

    print(data)
    print(news_list)
    params = {"index": news_list[i]}
    response_get = requests.get(url_get_news, headers=headers, params=params)
    data_news = response_get.json()
    print(data_news)
    dataResult = data_news["data"]["result"]

    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(types.InlineKeyboardButton(dataResult, callback_data="data_"))
    kb.add(
        types.InlineKeyboardButton("<<", callback_data=f"prev_{i}"),
        types.InlineKeyboardButton(">>", callback_data=f"next_{i}"),
    )

    user_id = callback_query.from_user.id
    await bot.edit_message_text(
        _("Topik"),
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        reply_markup=kb,
    )


@dp.message_handler(lambda message: message.text == _("Offers"), state=YourState.main)
async def handle_offers(message: types.Message, state: FSMContext):

    button1 = types.KeyboardButton(
        _("Wish"),
    )
    button2 = types.KeyboardButton(
        _("Complaint"),
    )
    button3 = types.KeyboardButton(
        _("Menu"),
    )
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    await message.answer(_("Choose type of offer"), reply_markup=keyboard)
    await YourState.feedback.set()


@dp.message_handler(lambda message: message.text == _("Wish"), state=YourState.feedback)
async def handle_wish(message: types.Message, state: FSMContext):  # noqa

    await message.answer(
        _("Write your wish please"), reply_markup=types.ReplyKeyboardRemove()
    )
    await YourState.waiting_for_feedback.set()


@dp.message_handler(lambda message: message.text, state=YourState.waiting_for_feedback)
async def handle_suggestion(message: types.Message):

    button1 = types.KeyboardButton(
        _("Menu"),
    )
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(button1)

    params = {
        "name": message.text,
        "type": "suggestions",
        "chat_id": message.chat.id,
        "socials": "telegram",
    }

    response = requests.post(url_new_thread, json=params, headers=headers)
    print(response.status_code)
    print(response.text)

    await message.answer(_("Thank you"), reply_markup=keyboard)
    await YourState.main.set()


@dp.message_handler(
    lambda message: message.text == _("Complaint"), state=YourState.feedback
)
async def handle_complaint(message: types.Message, state: FSMContext):  # noqa

    await message.answer(
        _("Write your complaint please"), reply_markup=types.ReplyKeyboardRemove()
    )
    await YourState.waiting_for_complain.set()


@dp.message_handler(lambda message: message.text, state=YourState.waiting_for_complain)
async def handle_feedback(message: types.Message, state: FSMContext):  # noqa

    button1 = types.KeyboardButton(
        _("Menu"),
    )
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(button1)
    params = {
        "name": message.text,
        "type": "feedback",
        "chat_id": message.chat.id,
        "socials": "telegram",
    }

    response = requests.post(url_new_thread, json=params, headers=headers)
    print(response.status_code)
    print(response.text)
    await message.answer(_("Thank you for your complaint"), reply_markup=keyboard)
    await YourState.main.set()



thread_num = None

@dp.message_handler(lambda message: message.text == _("Help"), state=YourState.main)
async def handle_help(message: types.Message, state: FSMContext):
    await message.answer("Help")
@dp.message_handler(lambda message: message.text == _("Support"), state=YourState.main)
async def start_command(message: types.Message):
    global thread_num
    button1 = types.KeyboardButton(
        _("Menu"),
    )
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(button1)
    params = {
        "name": message.text,
        "type": "issue",
        "chat_id": message.chat.id,
        "socials": "telegram",
    }

    response = requests.post(url_new_thread, json=params, headers=headers)
    print(response.json())
    thread_num = response.json()['data']['result']
    print(thread_num)
    await message.answer(_("Send your messge and we will responce you soon"),reply_markup=keyboard)
    await YourState.chat.set()


@dp.message_handler(lambda message: True, state=YourState.chat)
async def handle_message(message: types.Message):
    global thread_num

    user_id = message.from_user.id
    thread = thread_num
    token = TOKEN

    await send_message_to_websocket(message.text, user_id, thread, token)

@dp.message_handler(content_types=['photo'], state=YourState.chat)
async def handle_photo(message: types.Message):

    photo = message.photo[-1]
    photo_url = await photo.get_url()
    params = {
        "url": photo_url
    }

    response = requests.post(url_send_photo, params=params, headers=headers)
    if response.status_code == 200:
        await message.answer('Фотографію успішно відправлено на сервер')
    else:
        await message.answer('Сталася помилка при відправці фотографії на сервер')
    print(photo_url)
    
@dp.message_handler(content_types=['video'], state=YourState.chat)
async def handle_video(message: types.Message):
    video = message.video
    video_url = await video.get_url()
    params = {
        "url": video_url,
    }

    response = requests.post(url_send_video, params=params, headers=headers)
    if response.status_code == 200:
        await message.answer('Відео успішно відправлено на сервер')
    else:
        await message.answer('Сталася помилка при відправці відео на сервер')
    print(video_url)
