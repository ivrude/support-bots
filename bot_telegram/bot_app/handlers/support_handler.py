import requests
from aiogram import types
from aiogram.dispatcher import FSMContext

from ..app import dp, storage
from ..settings.configs import headers, url_new_thread
from .utils import YourState, _


@dp.message_handler(lambda message: message.text == _("Support"), state=YourState.main)
async def handle_support(message: types.Message):

    await message.answer(
        _("Write your issue please"), reply_markup=types.ReplyKeyboardRemove()
    )
    await YourState.waiting_for_issue.set()


@dp.message_handler(lambda message: message.text, state=YourState.waiting_for_issue)
async def handle_issue(message: types.Message, state: FSMContext):  # noqa

    params = {
        "name": message.text,
        "type": "issue",
        "chat_id": message.chat.id,
        "socials": "telegram",
    }

    response = requests.post(url_new_thread, json=params, headers=headers)
    print(response.status_code)
    print(response.text)
    button1 = types.KeyboardButton(
        _("Menu"),
    )
    keyboard = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(button1)
    await message.answer(_("Thank you for your issue.Wait"), reply_markup=keyboard)
    data_to_store = {"thread": {"thread": message.text, "thread_result": False}}
    await storage.update_data(
        chat=message.chat.id, user=message.from_user.id, data=data_to_store
    )
    await YourState.main.set()
