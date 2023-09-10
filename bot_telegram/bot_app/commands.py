import asyncio

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from email_validator import EmailNotValidError, validate_email

from .app import bot, dp, storage
from .settings.configs import (
    headers,
    url_check_email,
    url_check_number,
    url_email_code,
    url_get_news,
    url_new_thread,
    url_news_list,
)
from .settings.locale import (
    get_locale_middleware_sync,
    set_language,
    setup_locale_middleware,
)


async def reset_code(chat_id, user_id):
    await asyncio.sleep(60)
    stored_data = await storage.get_data(chat=chat_id, user=user_id)
    print(stored_data)
    code_check = int(stored_data["code"])
    if code_check != 0:
        data_to_store = {"code": 0}
        await storage.update_data(chat=chat_id, user=user_id, data=data_to_store)
        await YourState.waiting_for_email.set()
        await bot.send_message(
            chat_id=chat_id, text="Час вийшов, пройдіть аутентифікацію заново"
        )


async def thread(chat_id, user_id):
    await asyncio.sleep(60)
    stored_data = await storage.get_data(chat=chat_id, user=user_id)
    print(stored_data)
    result = stored_data["thread"]["thread_result"]
    if not result:
        await YourState.main.set()
        await bot.send_message(
            chat_id=chat_id, text="Час вийшов, комунікація завершена"
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


i18n = get_locale_middleware_sync(dp)
_ = i18n.gettext


@dp.message_handler(commands=["start"])
async def handle_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton("English", callback_data="lang_en"))
    keyboard.add(types.InlineKeyboardButton("Українська", callback_data="lang_uk"))
    keyboard.add(types.InlineKeyboardButton("Руский", callback_data="lang_ru"))

    await message.answer("Сhoose language:", reply_markup=keyboard)


# Get the user's language preference (replace this with your logic)


@dp.callback_query_handler(lambda query: query.data.startswith("lang_"))
async def language(callback_query: types.CallbackQuery):
    dataS = callback_query.data.split("_")
    selected_language = dataS[1]
    print(selected_language)

    user_id = callback_query.from_user.id

    data_to_store = {"language": selected_language}
    await storage.set_data(chat=user_id, user=user_id, data=data_to_store)

    await set_language(user_id, selected_language)

    await bot.send_message(user_id, _("Choosen language eanglish"))

    button1 = types.KeyboardButton(_("Phone number"), request_contact=True)
    button2 = types.KeyboardButton(_("Email"))
    button3 = types.KeyboardButton(_("Back"))
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    await bot.send_message(user_id, _("Choose how to auth"), reply_markup=keyboard)
    await YourState.waiting_for_contact.set()


@dp.message_handler(lambda message: message.text in ["Назад", "Back"], state="*")
async def handle_back(message: types.Message, state: FSMContext):
    await state.finish()
    await handle_start(message)


@dp.message_handler(
    lambda message: message.text in ["Phone number", "Номер телефону"],
    state=YourState.waiting_for_contact,
)
async def handle_phone_authorization(message: types.Message):
    await message.answer(
        "Авторизація за телефоном. Будь ласка, надішліть свій номер телефону.",
    )
    await YourState.waiting_for_contact.set()


@dp.message_handler(
    content_types=types.ContentTypes.CONTACT, state=YourState.waiting_for_contact
)
async def handle_contact_authorization(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(user_id, selected_language)
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

        response = requests.get(url_check_number, headers=headers, params=params)

        result = response.json()
        print(result)
        rez = result["status"]
        print(
            rez,
        )
        if rez == "error":
            await message.answer("Цього номера немає у базі.Перевірте дані уважно")
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
    lambda message: message.text in ["Email", "Імейл"],
    state=YourState.waiting_for_contact,
)
async def handle_email_choice(message: types.Message):

    await YourState.waiting_for_email.set()
    await message.answer(
        "Ви вибрали авторизацію за почтою. Будь ласка, введіть свій емейл."
    )


@dp.message_handler(lambda message: message.text, state=YourState.waiting_for_email)
async def handle_contact_email(message: types.Message):
    email = message.text
    try:
        validate_email(email)
        print("Email is valid")
    except EmailNotValidError as e:
        print(f"Email is not valid: {e}")
        await YourState.waiting_for_email.set()
        await message.answer("Електронну адресу введено неправильно.Повторіть спробу")
        return
    params = {"email": email, "chat_id": message.chat.id}

    response = requests.get(url_check_email, headers=headers, params=params)

    result = response.json()
    print(result)
    if result["status"] == "error":
        await YourState.waiting_for_email.set()
        await message.answer(
            "Цієї пошти немає у базі.Переконайтесь , що ви входите з потрібного акаунту"
        )
    else:

        params = {
            "email": email,
        }

        response1 = requests.post(url_email_code, params=params, headers=headers)
        data = response1.json()
        print(data)
        dataResult = data["data"]["result"]
        if dataResult == "error":
            await YourState.waiting_for_email.set()
            await message.answer(
                "Помилка відправлення.Будь ласка, переконайтесь ,"
                "що ввели все правильно і введіть свій email заново"
            )
            return
        else:

            data_to_store = {"code": dataResult}

            await storage.update_data(
                chat=message.from_user.id, user=message.from_user.id, data=data_to_store
            )
            asyncio.create_task(reset_code(message.chat.id, message.from_user.id))

        await YourState.waiting_for_code.set()
        await message.answer(
            "Вам був надісланий код підтвердження на вашу адресу електронної пошти. "
            "Будь ласка, введіть його."
        )


@dp.message_handler(
    lambda message: message.text.isdigit(), state=YourState.waiting_for_code
)
async def handle_code(message: types.Message):
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(message.from_user.id, selected_language)
    code = int(message.text)

    code_check = int(stored_data["code"])
    data_to_store = {"code": 0}
    await storage.update_data(
        chat=message.chat.id, user=message.from_user.id, data=data_to_store
    )
    if code_check != code:
        await YourState.waiting_for_email.set()
        await message.answer(
            "Не правильно. Будь ласка, переконайтесь ,"
            "що ввели все правильно і введіть свій email заново"
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
    lambda message: message.text in ["Меню", "Menu"],
    state=[
        YourState.waiting_for_feedback,
        YourState.feedback,
        YourState.main,
        YourState.offers,
        YourState.settings,
        YourState.menu,
    ],
)
async def handle_settings_ua(message: types.Message, state: FSMContext):
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(message.from_user.id, selected_language)
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


@dp.message_handler(
    lambda message: message.text in ["Settings", "Налаштування"], state=YourState.main
)
async def handle_settings_user(message: types.Message, state: FSMContext):  # noqa
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(message.from_user.id, selected_language)
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
    lambda message: message.text in ["Сповіщення", "Notifications"],
    state=YourState.settings,
)
async def handle_notifications_eng(message: types.Message, state: FSMContext):
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(message.from_user.id, selected_language)
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


@dp.message_handler(
    lambda message: message.text in ["News", "Новини"], state=YourState.main
)
async def handle_news(message: types.Message, state: FSMContext):
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(message.from_user.id, selected_language)
    await message.answer(_("This is list of our news"))

    response = requests.get(url_news_list, headers=headers)
    data = response.json()
    news_list = data["data"]["news"]
    print(data)
    print(news_list)
    i = 0
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

    # Отримайте id повідомлення та чату, щоб пізніше оновити повідомлення
    chat_id = message.chat.id
    msg_id = message.message_id

    await bot.send_message(chat_id, _("Topik"), reply_markup=kb)

    # Збережіть id повідомлення в стані
    await state.update_data(message_id=msg_id)
    await YourState.main.set()


@dp.callback_query_handler(
    lambda query: query.data.startswith("prev"), state=YourState.main
)
async def process_prev_button(callback_query: types.CallbackQuery, state: FSMContext):
    stored_data = await storage.get_data(
        chat=callback_query.from_user.id, user=callback_query.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(callback_query.from_user.id, selected_language)
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
    stored_data = await storage.get_data(
        chat=callback_query.from_user.id, user=callback_query.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(callback_query.from_user.id, selected_language)

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


@dp.message_handler(
    lambda message: message.text in ["Пропозиції", "Offers"], state=YourState.main
)
async def handle_offers(message: types.Message, state: FSMContext):
    stored_data = await storage.get_data(
        chat=message.from_user.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(message.from_user.id, selected_language)
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


@dp.message_handler(
    lambda message: message.text in ["Побажання", "Wish"], state=YourState.feedback
)
async def handle_wish(message: types.Message, state: FSMContext):  # noqa
    stored_data = await storage.get_data(
        chat=message.from_user.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(message.from_user.id, selected_language)
    await message.answer(
        _("Write your wish please"), reply_markup=types.ReplyKeyboardRemove()
    )
    await YourState.waiting_for_feedback.set()


@dp.message_handler(lambda message: message.text, state=YourState.waiting_for_feedback)
async def handle_suggestion(message: types.Message):
    stored_data = await storage.get_data(
        chat=message.from_user.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(message.from_user.id, selected_language)
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
    lambda message: message.text in ["Скарга", "Complaint"], state=YourState.feedback
)
async def handle_complaint(message: types.Message, state: FSMContext):  # noqa
    stored_data = await storage.get_data(
        chat=message.from_user.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(message.from_user.id, selected_language)
    await message.answer(
        _("Write your complaint please"), reply_markup=types.ReplyKeyboardRemove()
    )
    await YourState.waiting_for_complain.set()


@dp.message_handler(lambda message: message.text, state=YourState.waiting_for_complain)
async def handle_feedback(message: types.Message, state: FSMContext):  # noqa
    stored_data = await storage.get_data(
        chat=message.from_user.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(message.from_user.id, selected_language)
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


@dp.message_handler(
    lambda message: message.text in ["Support", "Техпідтримка"], state=YourState.main
)
async def handle_support(message: types.Message, state: FSMContext):
    stored_data = await storage.get_data(
        chat=message.from_user.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(message.from_user.id, selected_language)
    await message.answer(
        "Write your issue please", reply_markup=types.ReplyKeyboardRemove()
    )
    await YourState.waiting_for_issue.set()


@dp.message_handler(lambda message: message.text, state=YourState.waiting_for_issue)
async def handle_issue(message: types.Message, state: FSMContext):  # noqa
    stored_data = await storage.get_data(
        chat=message.from_user.id, user=message.from_user.id
    )
    print(stored_data)
    selected_language = stored_data["language"]

    await set_language(message.from_user.id, selected_language)
    params = {
        "name": message.text,
        "type": "issue",
        "chat_id": message.chat.id,
        "socials": "telegram",
    }

    response = requests.post(url_new_thread, json=params, headers=headers)
    print(response.status_code)
    print(response.text)
    await message.answer(_("Thank you for your issue.Wait"))
    data_to_store = {"thread": {"thread": message.text, "thread_result": False}}
    await storage.update_data(
        chat=message.chat.id, user=message.from_user.id, data=data_to_store
    )
    asyncio.create_task(thread(message.chat.id, message.from_user.id))


@dp.message_handler(
    lambda message: message.text in ["Help", "Допомога"], state=YourState.main
)
async def handle_help(message: types.Message, state: FSMContext):
    await message.answer("Help")
