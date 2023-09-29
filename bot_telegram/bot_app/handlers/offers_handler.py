import requests
from aiogram import types
from aiogram.dispatcher import FSMContext

from ..app import dp
from ..settings.configs import headers, url_new_thread
from .utils import YourState, _


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
    await YourState.waiting_for_wish.set()


@dp.message_handler(lambda message: message.text, state=YourState.waiting_for_wish)
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
