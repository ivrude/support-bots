import pymysql
import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import asyncio
from aiocron import crontab
from datetime import timedelta, datetime

API_TOKEN =("6542659135:AAEsVEDtZZwwazKRnTebiS3kVDr5CzTlumk")

DATABASE_HOST = 'mysql-138752-0.cloudclusters.net'
DATABASE_USER = 'admin'
DATABASE_PASSWORD = 'CtUfEulL'
DATABASE_NAME = 'themes'
DATABASE_PORT = 19653  # Замініть це значення на ваш змінений порт
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Set up logging (optional)
logging.basicConfig(level=logging.INFO)

# Function to get events for a given theme_id from the database
async def get_events_for_theme(theme_id):
    connection = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        port=DATABASE_PORT
    )
    cursor = connection.cursor()
    query = "SELECT title, description, date_time FROM meets_event WHERE theme_id=%s"
    cursor.execute(query, (theme_id,))
    data = cursor.fetchall()
    connection.close()

    events_for_theme = []
    for event in data:
        title, description, date_time = event
        events_for_theme.append(f"Title: {title}\nDescription: {description}\nTime: {date_time}\n")
    return events_for_theme

def get_phone_number_from_database(user_id):
    # Retrieve the user's phone number from the 'meets_client' table
    connection = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        port=DATABASE_PORT
    )
    cursor = connection.cursor()
    query = "SELECT phone_number FROM meets_client WHERE user_id=%s"
    cursor.execute(query, (user_id,))
    data = cursor.fetchone()
    connection.close()

    if data:
        return data[0]  # Return the phone number from the database
    else:
        return None


def save_response_to_database(phone_number, response, event_id):
    # Save the user's response and phone number to the 'meets_response' table
    connection = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        port=DATABASE_PORT
    )
    cursor = connection.cursor()

    # Check if a record for the user and event already exists
    query = "SELECT id FROM meets_responce WHERE phone_number=%s AND event_id=%s"
    cursor.execute(query, (phone_number, event_id))
    existing_record_id = cursor.fetchone()

    if existing_record_id:
        # Update the existing record
        query = "UPDATE meets_responce SET response=%s WHERE id=%s"
        cursor.execute(query, (response, existing_record_id[0]))
    else:
        # Create a new record
        query = "INSERT INTO meets_responce (phone_number, response, event_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (phone_number, response, event_id))

    connection.commit()
    connection.close()

@dp.message_handler(commands=["time"])
async def my_events(message: types.Message):
    user_id = message.from_user.id
    phone_number = get_phone_number_from_database(user_id)  # Замініть це на змінну з номером телефону користувача

    # Підключення до бази даних
    connection = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        port=DATABASE_PORT
    )
    cursor = connection.cursor()

    # Отримання поточного часу
    current_time = datetime.now()


    next_day_time = current_time + timedelta(hours=24)

    # Отримання івентів, на які користувач підписаний, і до яких залишилося менше ніж 24 години
    query = "SELECT DISTINCT e.title, e.date_time FROM meets_event e INNER JOIN meets_responce r ON e.event_id = r.event_id WHERE r.phone_number = %s AND r.response = 'yes' AND e.date_time <= DATE_ADD(NOW(), INTERVAL 27 HOUR) AND e.date_time >= %s AND e.date_time <= %s"
    cursor.execute(query, (phone_number, current_time, next_day_time))
    data = cursor.fetchall()
    connection.close()

    if data:
        response_message = "Your upcoming events:\n"
        for event_title, event_date in data:
            response_message += f"Event: {event_title}, Date: {event_date.strftime('%Y-%m-%d %H:%M')}\n"
    else:
        response_message = "You have no upcoming events in the next 24 hours."

    await message.answer(response_message)

async def handle_response(user_id, response, event_id):



    # Надсилання відповіді користувачеві
    response_message = ""
    phone_number = get_phone_number_from_database(user_id)

    # If the user's phone number is not registered, ask them to register first
    if not phone_number:
        await bot.send_message(user_id, "Будь ласка, зареєструйтесь спочатку, надіславши свій номер телефону.")
        return

    # Save or update the user's response and phone number in the database
    save_response_to_database(phone_number, response, event_id)

    if response == "yes":
        response_message = "Ви записались на захід!"
    elif response == "maybe":
        response_message = "Можливо, що будете на західі."
    elif response == "no":
        response_message = "Ви не будете присутні на західі."

    await bot.send_message(user_id, response_message)
def is_phone_number_registered(phone_number):
    # Check if the phone number already exists in the 'meets_client' table
    connection = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        port=DATABASE_PORT
    )
    cursor = connection.cursor()
    query = "SELECT phone_number FROM meets_client WHERE phone_number=%s"
    cursor.execute(query, (phone_number,))
    data = cursor.fetchone()
    connection.close()

    return data is not None

async def get_event_id_for_theme(theme_id):
    connection = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        port=DATABASE_PORT
    )
    cursor = connection.cursor()
    query = "SELECT event_id FROM meets_event WHERE theme_id=%s"
    cursor.execute(query, (theme_id,))
    data = cursor.fetchall()
    connection.close()

    event_ids = [event[0] for event in data]
    return event_ids

# Function to get events for which the user has responded 'yes'
async def get_registered_events(phone_number):
    connection = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        port=DATABASE_PORT
    )
    cursor = connection.cursor()
    query = "SELECT event_id FROM meets_responce WHERE phone_number=%s AND response='yes'"
    cursor.execute(query, (phone_number,))
    data = cursor.fetchall()
    connection.close()

    event_ids = [event[0] for event in data]
    return event_ids


def add_phone_number_to_database(user_id, phone_number):
    # Add the phone number to the 'meets_client' table
    connection = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        port=DATABASE_PORT
    )
    cursor = connection.cursor()
    query = "INSERT INTO meets_client (user_id, phone_number) VALUES (%s, %s)"
    cursor.execute(query, (user_id, phone_number))
    connection.commit()
    connection.close()

@dp.message_handler(commands=['my_events'])
async def handle_my_events(message: types.Message):
    user_id = message.from_user.id
    phone_number = get_phone_number_from_database(user_id)

    if not phone_number:
        await message.answer("Будь ласка, зареєструйтесь спочатку, надіславши свій номер телефону.")
        return

    registered_event_ids = await get_registered_events(phone_number)

    connection = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        port=DATABASE_PORT
    )
    cursor = connection.cursor()

    events_info = []
    for event_id in registered_event_ids:
        query = "SELECT title, description, date_time FROM meets_event WHERE event_id=%s"
        cursor.execute(query, (event_id,))
        data = cursor.fetchone()
        if data:
            title, description, date_time = data
            events_info.append(f"Title: {title}\nDescription: {description}\nTime: {date_time}\n")

    connection.close()

    if events_info:
        events_info_text = "\n".join(events_info)
        response_message = f"Ви зареєстровані на наступні заходи:\n{events_info_text}"
    else:
        response_message = "Ви не зареєстровані на жоден захід."

    await message.answer(response_message)

@dp.message_handler(commands=['start'])
async def handle_register(message: types.Message,):
    button = types.KeyboardButton("Зареєструватись", request_contact=True)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(button)

    await message.answer("Будь ласка, надішліть свій номер телефону:", reply_markup=keyboard)

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def handle_contact(message: types.Message):
    phone_number = message.contact.phone_number
    user_id = message.contact.user_id
    if user_id != message.from_user.id:
        await message.answer("Ви намагаєтеся зареєструвати інший номер телефону.")
        return
    elif not is_phone_number_registered(phone_number):
        add_phone_number_to_database(user_id, phone_number)
        await message.answer("Ваш номер телефону був успішно зареєстрований в базі даних. Щоб подивитись усі команди натисність /help",reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("Ваш номер телефону вже зареєстрований в базі даних. Щоб подивитись усі команди натисніть /help",reply_markup=types.ReplyKeyboardRemove())

# Handler for the /start command
@dp.message_handler(commands=['theme'])
async def handle_start(message: types.Message):
    # Your database query to get themes
    connection = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME,
        port=DATABASE_PORT
    )
    cursor = connection.cursor()
    query = "SELECT id, name FROM meets_theme"
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()

    # Create the keyboard with buttons for each theme
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for theme_id, theme_name in data:
        button = types.InlineKeyboardButton(theme_name, callback_data=f"theme_{theme_id}")
        keyboard.add(button)

    # Send the keyboard to the user
    await message.reply("Оберіть тему:", reply_markup=keyboard)


@dp.message_handler(commands=['help'])
async def start_command(message: types.Message):

    # List of available commands
    commands_list = (
        "/help - Get a  list of commands\n"
        "/time - Get a list of your upcoming events within the next 24 hours\n"
        "/my_events - Get a list of event you are going to come\n"
        "/start - Registration\n"
        "/theme - get a list of all themes\n"
    )

    # Send the greeting and command list
    await message.answer("Here are the available commands:\n" + commands_list)

# Handler for the button callbacks
@dp.callback_query_handler(lambda c: c.data)
async def callback_handler(callback_query: types.CallbackQuery):
    data = callback_query.data.split("_")
    user_id = callback_query.from_user.id  # Get the user_id

    if data[0] == "theme":  # Theme selection
        theme_id = int(data[1])
        event_ids = await get_event_id_for_theme(theme_id)

        # Send the available events with response buttons
        events_for_theme = await get_events_for_theme(theme_id)
        for i, event in enumerate(events_for_theme):
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            event_id = event_ids[i]
            button1 = types.InlineKeyboardButton("Записатись", callback_data=f"yes_{event_id}")  # Use event_id in callback data
            button2 = types.InlineKeyboardButton("Можливо буду", callback_data=f"maybe_{event_id}")  # Use event_id in callback data
            button3 = types.InlineKeyboardButton("Не прийду", callback_data=f"no_{event_id}")  # Use event_id in callback data
            keyboard.add(button1, button2, button3)

            await bot.send_message(user_id, event, reply_markup=keyboard)
            await asyncio.sleep(1)

    elif data[0] in ['yes', 'maybe', 'no']:  # Response selection
        response = data[0]
        event_id = int(data[1])  # Get the event_id
        await handle_response(user_id, response, event_id)

    else:
        # Invalid data
        await bot.send_message(user_id, "Недійсні дані.")



# Start the bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)