import json

import requests
from aiogram import types

from ..app import dp, storage
from ..settings.configs import  headers, url_send_raiting
from .utils import YourState, _


async def send_message_to_websocket(
    message, user_id, thread_id, token, type, language, chat_status
):
    websocket_connection = dp.data["websocket_connection"]
    data = {
        "message": message,
        "user_id": user_id,
        "thread_id": thread_id,
        "token": token,
        "type": type,
        "language": language,
        "chat_status": chat_status,
    }
    message_json = json.dumps(data)
    await websocket_connection.send(message_json)


@dp.message_handler(
    lambda message: message.text == _("Menu"),
    state=[
        YourState.waiting_for_wish,
        YourState.feedback,
        YourState.main,
        YourState.offers,
        YourState.settings,
        YourState.menu,
        YourState.chat,
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
        row_width=3, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(*buttons)

    await message.answer(_("Choose menu punkt"), reply_markup=keyboard)
    await YourState.main.set()


@dp.message_handler(
    lambda message: message.text == _("End chating"),
    state=[
        YourState.chat,
    ],
)
async def handle_mark(message: types.Message):
    buttons = [
        types.KeyboardButton(text="1"),
        types.KeyboardButton(text="2"),
        types.KeyboardButton(text="3"),
        types.KeyboardButton(text="4"),
        types.KeyboardButton(text="5"),
        types.KeyboardButton(text=_("Menu")),
    ]
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    print(stored_data)
    keyboard = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(*buttons)
    #token = TOKEN_DOMAIN
    #thread = stored_data.get("thread_num")
    #language = stored_data.get("language")
    #user_id = message.from_user.id
    #type = "close_thread"
    #chat_status = "chat_status"

    await message.answer(_("Please rate the agent work"), reply_markup=keyboard)
    #await send_message_to_websocket(
    #    message.text, user_id, thread, token, type, language, chat_status
    #)

def send_agent_rating(thread_num, raiting):
    params = {
        "raiting": int(raiting),  # Оцінка від 1 до 5
        "thread_num": int(thread_num),
    }
    response = requests.post(url_send_raiting, params=params, headers=headers)
    print(params)
    print(response.json())
    if response.status_code == 200:
        print("Rating saved successfully")
    else:
        print("Error saving rating")


@dp.message_handler(
    lambda message: message.text in ["1", "2", "3", "4", "5"], state=YourState.chat
)
async def handle_rating(message: types.Message):
    user_id = message.from_user.id
    stored_data = await storage.get_data(chat=user_id, user=user_id)
    thread_num = stored_data.get("thread_num")
    raiting = message.text
    print(raiting)

    send_agent_rating(thread_num, raiting)
    await message.answer(_("Thanks for your mark!"))

    await handle_settings_ua(message)
