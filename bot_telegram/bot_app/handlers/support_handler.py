import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
import json
from ..app import dp, storage
from ..settings.configs import headers, url_new_thread, TOKEN, url_send_photo, url_send_video
from .utils import YourState, _
async def send_message_to_websocket(message, user_id, thread,token, photo=None):
    websocket_connection = dp.data['websocket_connection']

    data = {"message": message, "user_id": user_id, "thread": thread, "token":token}



    message_json = json.dumps(data)
    await websocket_connection.send(message_json)


thread_num = None


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
    # Тут ви можете додатково обробляти фото або виконувати необхідні дії

# Додавання обробника для відео
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
