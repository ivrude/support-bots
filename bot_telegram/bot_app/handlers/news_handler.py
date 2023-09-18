import requests
from aiogram import types
from aiogram.dispatcher import FSMContext

from ..app import bot, dp
from ..settings.configs import headers, url_get_news, url_news_list
from .utils import YourState, _


@dp.message_handler(lambda message: message.text == _("News"), state=YourState.main)
async def handle_news(message: types.Message, state: FSMContext):

    await message.answer(_("This is list of our news"))

    response = requests.get(url_news_list, headers=headers)
    data = response.json()
    news_list = data["data"]["news"]
    print(data)
    print(news_list)
    i = 0
    if len(news_list) > 0:
        params = {"index": news_list[i]}
    else:
        await message.answer(_("This is empty"))
        return

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
