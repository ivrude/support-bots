from aiogram import Bot, types,Dispatcher
from aiohttp import web
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN =("6059087374:AAEg4bLEIJqF-PFkjwfIDeOSbESRrJsvvLs")
bot = Bot(token=TOKEN)

storage = MemoryStorage()
dp=Dispatcher(bot, storage=storage)
app=web.Application()
webhook_path=f'/{TOKEN}'
Bot.set_current(bot)


class YourState(StatesGroup):
    waiting_for_contact = State()
    waiting_for_email = State()
    waiting_for_code = State()

async def set_webhook():
    webhook_url=f'https://b34a-85-114-213-169.ngrok.io{webhook_path}'
    print(webhook_url)
    await bot.set_webhook(webhook_url)
async def on_startup(_):
    await set_webhook()

@dp.message_handler(commands=['start'])
async def handle_register(message: types.Message, state: FSMContext):
    button1 = types.KeyboardButton("Авторизуватись за телефоном", request_contact=True, callback_data="button1")
    button2 = types.KeyboardButton("Авторизуватись за почтою",)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(button1)
    keyboard.add(button2)
    await YourState.waiting_for_contact.set()

    await message.answer("Будь ласка, виберіть як зареєструватись:", reply_markup=keyboard)

@dp.callback_query_handler(text="button1", state=YourState.waiting_for_contact)
async def handle_phone_authorization(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Ви натиснули авторизацію за телефоном. Будь ласка, надішліть свій номер телефону.")
    await state.update_data(prev_state=state.current_state)
    await YourState.waiting_for_contact.set()

@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=YourState.waiting_for_contact)
async def handle_contact_authorization(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id != message.contact.user_id:
        await message.answer("Ви намагаєтеся авторизувати інший номер телефону.")
        return
    else:
        await message.answer("Ви успішно авторизувались за допомогою номера телефону.", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()
    await show_buttons(message.from_user.id)

@dp.message_handler(lambda message: message.text == "Авторизуватись за почтою", state=YourState.waiting_for_contact)
async def handle_email_choice(message: types.Message, state: FSMContext):
    await YourState.waiting_for_email.set()
    await message.answer("Ви вибрали авторизацію за почтою. Будь ласка, введіть свій емейл.",reply_markup=types.ReplyKeyboardRemove())

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
    await show_buttons(message.from_user.id)

async def show_buttons(user_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button1 = types.KeyboardButton("Виберіть мову")
    button2 = types.KeyboardButton("B2")
    button3 = types.KeyboardButton("B3")
    keyboard.add(button1)
    keyboard.add(button2)
    keyboard.add(button3)
    await bot.send_message(user_id, "Ось ваші кнопки:", reply_markup=keyboard)








async def handle_webhook(request):
    print('333')
    url= str(request.url)
    index=url.rfind('/')
    token=url[index+1:]

    if token==TOKEN:
        request_data = await request.json()
        update=types.Update(**request_data)
        await dp.process_update(update)
        return web.Response()
    else:
        return web.Response(status=403)


from aiogram.dispatcher.webhook import get_new_configured_app
app.router.add_post(f'/{TOKEN}',handle_webhook)
if __name__=='__main__':
    app = get_new_configured_app(dispatcher=dp, path=webhook_path)
    app.on_startup.append(on_startup)
    web.run_app(
        app,
        host='0.0.0.0',
        port=5000,
    )


