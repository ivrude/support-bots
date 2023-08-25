from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

from bot.src.bot_app.settings.locale import setup_locale_middleware, set_language

from bot.src.bot_app import  bot, dp


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
    waiting_for_language = State()
i18n = setup_locale_middleware(dp)
_ = i18n.gettext

@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton("English", callback_data='lang_en'))
    keyboard.add(types.InlineKeyboardButton("Українська", callback_data='lang_uk'))
    await message.answer("Сhoose language:", reply_markup=keyboard)

# Get the user's language preference (replace this with your logic)



@dp.callback_query_handler(lambda query: query.data.startswith('lang_'))
async def language(callback_query: types.CallbackQuery):
    dataS = callback_query.data.split('_')
    selected_language = dataS[1]
    await set_language(selected_language)
    print(selected_language)
    user_id = callback_query.from_user.id
    user_data = {"selected_language": selected_language}
    await dp.current_state(user=user_id).update_data(user_data=user_data)



    await bot.send_message(user_id, _("Choosen language eanglish"))

    button1 = types.KeyboardButton(_("Phone number"), request_contact=True)
    button2 = types.KeyboardButton(_("Email"))
    button3 = types.KeyboardButton(_("Back"))
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    await bot.send_message(user_id, _("Choose how to auth"), reply_markup=keyboard)
    await dp.current_state(user=user_id).update_data(user_data=user_data)
    await YourState.waiting_for_contact.set()
@dp.message_handler(lambda message: message.text in ["Назад", "Back"], state="*")
async def handle_back(message: types.Message, state: FSMContext):
    await state.finish()
    await handle_start(message)

@dp.message_handler(lambda message: message.text in ["Phone number", "Номер телефону"], state=YourState.waiting_for_contact)
async def handle_phone_authorization(message: types.Message, state: FSMContext):
    await state.update_data(prev_state=state.current_state)
    await YourState.waiting_for_contact.set()

@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=YourState.waiting_for_contact)
async def handle_contact_authorization(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    selected_language = user_data['user_data']['selected_language']
    await set_language(selected_language)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(_("Back"))
    user_id = message.from_user.id
    if user_id != message.contact.user_id:
        await message.answer(_("You are trying to use not your number"),reply_markup=keyboard)
        return
    else:
        await message.answer(_("You sucsesful autorised"), reply_markup=types.ReplyKeyboardRemove())
        print(selected_language)
        buttons = [
            types.KeyboardButton(text=_("Menu")),
        ]

        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(*buttons)

        await message.answer(_("Choose above"), reply_markup=keyboard)
        await YourState.main.set()



@dp.message_handler(lambda message: message.text == "Авторизуватись за почтою", state=YourState.waiting_for_contact)
async def handle_email_choice(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    selected_language = user_data['user_data']['selected_language']
    await YourState.waiting_for_email.set()
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton(language_phrases[selected_language]['back']))
    await message.answer("Ви вибрали авторизацію за почтою. Будь ласка, введіть свій емейл.", reply_markup=keyboard)
@dp.message_handler(lambda message: message.text, state=YourState.waiting_for_email)
async def handle_contact_email(message: types.Message, state: FSMContext):
    email = message.text
    # Ваша логіка для збереження емейлу тут
    await YourState.waiting_for_code.set()
    await message.answer("Вам був надісланий код підтвердження на вашу адресу електронної пошти. Будь ласка, введіть його.")

@dp.message_handler(lambda message: message.text.isdigit(), state=YourState.waiting_for_code)
async def handle_code(message: types.Message, state: FSMContext):
    code = message.text
    # Ваша логіка для перевірки коду тут
    await state.finish()
    await message.answer("Авторизація завершена. Ви успішно увійшли за допомогою електронної пошти.",)
    user_data = await state.get_data()
    selected_language = user_data['user_data']['selected_language']

    buttons = [
        types.KeyboardButton(text=language_phrases[selected_language]['button']),
    ]
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons)

    await message.answer(language_phrases[selected_language]['menu'], reply_markup=keyboard)
    await YourState.main.set()


@dp.message_handler(lambda message: message.text in ["Меню", "Menu"],state=[YourState.waiting_for_feedback,YourState.feedback,YourState.main,YourState.offers,YourState.settings,YourState.menu])
async def handle_settings_ua(message: types.Message,state: FSMContext):
    user_data = await state.get_data()
    print(user_data)
    selected_language = user_data['user_data']['selected_language']
    print(user_data)
    await set_language(selected_language)
    buttons = [
        types.KeyboardButton(text=_("News")),
        types.KeyboardButton(text=_("Settings")),
        types.KeyboardButton(text=_("Offers")),
        types.KeyboardButton(text=_("Help")),
        types.KeyboardButton(text=_("Support"))
    ]

    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons)

    await message.answer(_("Choose menu punkt"), reply_markup=keyboard)
    await YourState.main.set()
@dp.message_handler(lambda message: message.text in ["Settings", "Налаштування"],state=YourState.main)
async def handle_settings_ua(message: types.Message,state: FSMContext):
    user_data = await state.get_data()
    selected_language = user_data['user_data']['selected_language']
    await set_language(selected_language)
    button1 = types.KeyboardButton(_("Profile"))
    button2 = types.KeyboardButton(_("Notifications") )
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(button1)
    keyboard.add(button2)
    await message.answer(_("Choose above"), reply_markup=keyboard)
    await YourState.settings.set()
@dp.message_handler(lambda message: message.text in ["Сповіщення", "Notifications"],state=YourState.settings)
async def handle_notifications_eng(message: types.Message,state: FSMContext):
    user_data = await state.get_data()
    selected_language = user_data['user_data']['selected_language']
    await set_language(selected_language)
    button1 = types.KeyboardButton(_("Get Notifications"))
    button2 = types.KeyboardButton(_("Dont get Notifications"))
    button3 = types.KeyboardButton(_("Menu"))
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    await message.answer(_("Choose above"),reply_markup=keyboard)

    await YourState.main.set()


@dp.message_handler(lambda message: message.text in ["News", "Новини"], state=YourState.main)
async def handle_news(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    selected_language = user_data['user_data']['selected_language']
    await set_language(selected_language)
    await message.answer(_("This is list of our news"))

    data = ['1', '5', '2', '3']
    i = 0
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton(data[i], callback_data='data_' + data[i]))
    kb.add(
        types.InlineKeyboardButton('<<', callback_data=f'prev_{i}'),
        types.InlineKeyboardButton('>>', callback_data=f'next_{i}')
    )

    # Отримайте id повідомлення та чату, щоб пізніше оновити повідомлення
    chat_id = message.chat.id
    msg_id = message.message_id

    await bot.send_message(chat_id, _("Topik"), reply_markup=kb)

    # Збережіть id повідомлення в стані
    await state.update_data(message_id=msg_id)
    await YourState.main.set()

@dp.callback_query_handler(lambda query: query.data.startswith('prev'), state=YourState.main)
async def process_prev_button(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    selected_language = user_data['user_data']['selected_language']
    await set_language(selected_language)
    data = ['1', '5', '2', '3']
    dataS = callback_query.data.split('_')
    i = int(dataS[1]) - 1

    if i < 0:
        i = len(data) - 1
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton(data[i], callback_data='data_' + data[i]))
    kb.add(
        types.InlineKeyboardButton('<<', callback_data=f'prev_{i}'),
        types.InlineKeyboardButton('>>', callback_data=f'next_{i}')
    )

    user_id = callback_query.from_user.id
    await bot.edit_message_text(_("Topik"), chat_id=user_id, message_id=callback_query.message.message_id, reply_markup=kb)
@dp.callback_query_handler(lambda query: query.data.startswith('next'), state=YourState.main)
async def process_next_button(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    selected_language = user_data['user_data']['selected_language']
    await set_language(selected_language)
    data = ['1', '5', '2', '3']
    dataS = callback_query.data.split('_')
    i = int(dataS[1]) + 1
    if i > len(data) - 1:
        i = 0
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton(data[i], callback_data='data_' + data[i]))
    kb.add(
        types.InlineKeyboardButton('<<', callback_data=f'prev_{i}'),
        types.InlineKeyboardButton('>>', callback_data=f'next_{i}')
    )

    user_id = callback_query.from_user.id
    await bot.edit_message_text(_("Topik"), chat_id=user_id, message_id=callback_query.message.message_id, reply_markup=kb)

@dp.message_handler(lambda message: message.text in ["Пропозиції", "Offers"],state=YourState.main)
async def handle_settings_ua(message: types.Message,state: FSMContext):
    user_data = await state.get_data()
    selected_language = user_data['user_data']['selected_language']
    await set_language(selected_language)
    button1 = types.KeyboardButton(_("Wish"), )
    button2 = types.KeyboardButton(_("Complaint"), )
    button3 = types.KeyboardButton(_("Menu"), )
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    await message.answer(_("Choose type of offer"), reply_markup=keyboard)
    await YourState.feedback.set()
@dp.message_handler(lambda message: message.text in ["Побажання", "Wish"],state=YourState.feedback)
async def handle_notifications_eng(message: types.Message,state: FSMContext):
    user_data = await state.get_data()
    selected_language = user_data['user_data']['selected_language']
    await set_language(selected_language)
    await message.answer(_("Write your wish please"),reply_markup=types.ReplyKeyboardRemove())
    await YourState.waiting_for_feedback.set()
@dp.message_handler(lambda message: message.text, state=YourState.waiting_for_feedback)
async def handle_wish(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    selected_language = user_data['user_data']['selected_language']
    await set_language(selected_language)
    button1 = types.KeyboardButton(_("Menu"), )
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(button1)
    await message.answer(_("Thank you for your wishes"),reply_markup=keyboard)
    await YourState.main.set()

@dp.message_handler(lambda message: message.text in ["Скарга", "Complaint"],state=YourState.feedback)
async def handle_notifications_eng(message: types.Message,state: FSMContext):
    user_data = await state.get_data()
    selected_language = user_data['user_data']['selected_language']
    await set_language(selected_language)
    await message.answer(_("Write your complaint please"),reply_markup=types.ReplyKeyboardRemove())
    await YourState.waiting_for_feedback.set()
@dp.message_handler(lambda message: message.text, state=YourState.waiting_for_feedback)
async def handle_contact_email(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    selected_language = user_data['user_data']['selected_language']
    await set_language(selected_language)
    button1 = types.KeyboardButton(_("Menu"), )
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(button1)
    await message.answer(_("Thank you for your complaint"), reply_markup=keyboard)
    await YourState.main.set()




