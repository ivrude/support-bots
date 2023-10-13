import asyncio
import json

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext

from ..app import dp, storage, bot
from ..settings.configs import (
    TOKEN_DOMAIN,
    headers,
    url_new_thread,
    url_send_photo,
    url_send_video,
    url_get_id,
)
from .utils import YourState, _

websocket_lock = asyncio.Lock()
is_handling_message = False
async def send_message_to_websocket(
    message, user_id, thread_id, token, type, language, chat_status, files, tg_id
):
    websocket_connection = dp.data["websocket_connection"]
    global is_handling_message
    data = {
        "type": type,
        "language": language,
        "message_text": message,
        "user": user_id,
        "token": token,
        "thread_id": thread_id,
        "chat_status": chat_status,
        "files": files,
        "tg_id": "Bot"
    }
    print(data)

    dp.data["message"]=data["message_text"]
    message_json = json.dumps(data)
    is_handling_message = False
    await websocket_connection.send(message_json)


async def receive_message_from_websocket(websocket):
    async with websocket_lock:
        json_data = await websocket.recv()
        data = json.loads(json_data)
        print(1)
        print(data)
        user = data.get('user','')
        thread_id = str(data.get('thread_id',''))
        user_temp = dp.data[thread_id]
        thread_num = dp.data[user_temp]
        source = data.get('tg_id','')
        print(user)
        print(user_temp)

        print(thread_id)
        print(thread_num)
        print(type(thread_id))
        print(type(thread_num))
        if thread_id == thread_num:
            if user != dp.data["user_id"]:
                message = data.get('message', '')
                if source == "Bot":
                    return None
                else:
                    await bot.send_message(text = message, chat_id=user_temp)
            else:
                return None
        else:
            return None




@dp.message_handler(lambda message: message.text == _("Support"), state=YourState.main)
async def start_command(message: types.Message, state: FSMContext):
    global is_handling_message
    user = message.from_user.id
    print(f'user1{user}')
    button1 = types.KeyboardButton(
        _("End chating"),
    )
    button2 = types.KeyboardButton(
        _("Menu"),
    )
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(button1)
    keyboard.add(button2)
    params = {
        "name": message.text,
        "type": "issue",
        "chat_id": message.chat.id,
        "socials": "telegram",
    }
    response = requests.post(url_new_thread, json=params, headers=headers)
    print(response.json())
    thread_num = response.json()["data"]["result"]
    dp.data[user] = thread_num
    data_to_store = {"thread_num": thread_num}
    await storage.update_data(chat=user, user=user, data=data_to_store)

    param = {
        "id_u": user
    }
    responce = requests.post(url_get_id, params=param, headers=headers)
    print(responce)
    user_id = responce.json()["data"]["result"]
    dp.data["user_id"] = user_id
    dp.data[thread_num] = user

    data_to_storage = {"user_id": user_id,thread_num:user}
    await storage.update_data(chat=user, user=user, data=data_to_storage)
    await message.answer(
        _("Send your messge and we will responce you soon"), reply_markup=keyboard
    )
    message_temp = "conect"
    token = TOKEN_DOMAIN
    language = "en"
    type = "chat_message"
    files = None
    chat_status = "active_chat"
    await send_message_to_websocket(
        message=message_temp, user_id=user_id, thread_id=thread_num, token=token, type=type, language=language, chat_status=chat_status, files=files, tg_id=user
    )
    await YourState.chat.set()
    print("yes")

    while True:
        try:
            if not is_handling_message:  # Перевірити, чи не обробляється вже повідомлення
                is_handling_message = True  # Встановити флаг активності обробки повідомлення
                print(user_id)
                await receive_message_from_websocket(dp.data["websocket_connection"])

            else:
                await asyncio.sleep(1)  # Якщо повідомлення вже обробляється, почекати 1 секунду
        except Exception as e:
            print(Exception)
            print(f"Error receiving message from websocket: {e}")
            await asyncio.sleep(1)
        finally:
            is_handling_message = False



@dp.message_handler(lambda message: True, state=YourState.chat)
async def handle_message(message: types.Message):
    type = "chat_message"

    user = message.from_user.id
    tg_id =user
    stored_data = await storage.get_data(chat=user, user=user)
    user_id = stored_data.get("user_id")
    print(user_id)
    thread_num = stored_data.get("thread_num")
    thread = thread_num
    token = TOKEN_DOMAIN
    files = None
    stored_data = await storage.get_data(
        chat=user, user=user
    )
    language = stored_data.get("language")
    print(language)
    chat_status = "active_chat"
    await send_message_to_websocket(
        message.text, user_id, thread, token, type, language, chat_status, files, tg_id
    )


@dp.message_handler(content_types=["photo"], state=YourState.chat)
async def handle_photo(message: types.Message):
    type = "chat_message"

    photo = message.photo[-1]
    photo_url = await photo.get_url()
    user_id = message.from_user.id
    stored_data = await storage.get_data(chat=user_id, user=user_id)
    thread_num = stored_data.get("thread_num")
    params = {"url": photo_url,"user_id": user_id, "thread_num":thread_num}

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
    token = TOKEN_DOMAIN
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
    if not message.caption:
        message = ""
    else :
        message = message.caption

    await send_message_to_websocket(
        message, user_id, thread, token, type, language, chat_status, files
    )

    # Тут ви можете додатково обробляти фото або виконувати необхідні дії


# Додавання обробника для відео
@dp.message_handler(content_types=["video"], state=YourState.chat)
async def handle_video(message: types.Message):
    user = message.from_user.id
    stored_data = await storage.get_data(chat=user, user=user)
    user_id = stored_data.get("user_id")
    thread_num = stored_data.get("thread_num")
    type = "chat_message"
    video = message.video
    video_url = await video.get_url()
    params = {
        "url": video_url,
        "user_id": user_id,
        "thread_num": thread_num
    }

    response = requests.post(url_send_video, params=params, headers=headers)
    if response.status_code == 200:
        await message.answer(_("The video has been successfully sent to the server"))
    else:
        await message.answer(
            _("An error occurred while sending the video to the server")
        )

    thread = thread_num
    token = TOKEN_DOMAIN
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
    if not message.caption:
        message = ""
    else:
        message = message.caption

    await send_message_to_websocket(
        message, user_id, thread, token, type, language, chat_status, files
    )
