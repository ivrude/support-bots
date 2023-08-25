from typing import Tuple, Any, Optional

from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
LOCALE_DOMAIN = "messages"
LOCALE_DIR = BASE_DIR / "locale"

language = ['en']


async def set_language(lang: str):
    global language
    language = lang


async def get_lang(user_id: int) -> str:
    return language


class LocaleMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        lang = await get_lang(1)
        print(lang)
        return lang


def setup_locale_middleware(dp):
    i18n = LocaleMiddleware(LOCALE_DOMAIN, LOCALE_DIR)
    dp.middleware.setup(i18n)
    return i18n
