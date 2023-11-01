
from aiogram.utils import executor


from bot_app import TOKEN, app, bot, dp

if __name__ == "__main__":

    executor.start_polling(dp, )
