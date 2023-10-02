import json

import requests
from aiogram import types


from ..app import dp, storage
from ..settings.configs import (
    TOKEN,
    headers,
    url_new_thread,
    url_send_photo,
    url_send_video,
    url_get_id,
)
from .utils import YourState, _


async def send_message_to_websocket(
    message, user_id, thread_id, token, type, language, chat_status, files
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
        "files": files,
    }
    message_json = json.dumps(data)
    await websocket_connection.send(message_json)


@dp.message_handler(lambda message: message.text == _("Support"), state=YourState.main)
async def start_command(message: types.Message):
    user = message.from_user.id
    button1 = types.KeyboardButton(
        _("End chating"),
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
    thread_num = response.json()["data"]["result"]
    print(thread_num)
    data_to_store = {"thread_num": thread_num}
    await storage.update_data(chat=user, user=user, data=data_to_store)
    param = {
        "id_u": user
    }
    responce = requests.post(url_get_id, params=param, headers=headers)
    print(responce)
    user_id = responce.json()["data"]["result"]
    print(user_id)
    data_to_storage = {"user_id": user_id}
    await storage.update_data(chat=user, user=user, data=data_to_storage)
    await message.answer(
        _("Send your messge and we will responce you soon"), reply_markup=keyboard
    )
    await YourState.chat.set()


@dp.message_handler(lambda message: True, state=YourState.chat)
async def handle_message(message: types.Message):
    type = "chat_message"

    user = message.from_user.id
    stored_data = await storage.get_data(chat=user, user=user)
    user_id = stored_data.get("user_id")
    print(user_id)
    thread_num = stored_data.get("thread_num")
    thread = thread_num
    token = TOKEN
    files = None
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    language = stored_data.get("language")
    print(language)
    chat_status = "active_chat"

    await send_message_to_websocket(
        message.text, user_id, thread, token, type, language, chat_status, files
    )


@dp.message_handler(content_types=["photo"], state=YourState.chat)
async def handle_photo(message: types.Message):
    type = "chat_message"

    photo = message.photo[-1]
    photo_url = await photo.get_url()
    params = {"url": photo_url}

    response = requests.post(url_send_photo, params=params, headers=headers)

    if response.status_code == 200:
        await message.answer(_("The photo has been successfully sent to the server"))
    else:
        await message.answer(
            _("An error occurred while sending the photo to the server")
        )
    print(photo_url)
    user = message.from_user.id
    stored_data = await storage.get_data(chat=user, user=user)
    user_id = stored_data.get("user_id")
    thread_num = stored_data.get("thread_num")
    thread = thread_num
    token = TOKEN
    file_id = response.json()["data"]["result"]
    files = [
        {"id": file_id},
    ]
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    language = stored_data.get("language")
    print(language)
    chat_status = "active_chat"
    message = message.caption

    await send_message_to_websocket(
        message, user_id, thread, token, type, language, chat_status, files
    )

    # Тут ви можете додатково обробляти фото або виконувати необхідні дії


# Додавання обробника для відео
@dp.message_handler(content_types=["video"], state=YourState.chat)
async def handle_video(message: types.Message):
    type = "chat_message"
    video = message.video
    video_url = await video.get_url()
    params = {
        "url": video_url,
    }

    response = requests.post(url_send_video, params=params, headers=headers)
    if response.status_code == 200:
        await message.answer(_("The video has been successfully sent to the server"))
    else:
        await message.answer(
            _("An error occurred while sending the video to the server")
        )
    user = message.from_user.id
    stored_data = await storage.get_data(chat=user, user=user)
    user_id = stored_data.get("user_id")
    thread_num = stored_data.get("thread_num")
    thread = thread_num
    token = TOKEN
    file_id = response.json()["data"]["result"]
    files = [
        {"id": file_id},
    ]
    stored_data = await storage.get_data(
        chat=message.chat.id, user=message.from_user.id
    )
    language = stored_data.get("language")
    print(language)
    chat_status = "active_chat"
    message = message.caption

    await send_message_to_websocket(
        message, user_id, thread, token, type, language, chat_status, files
    )
