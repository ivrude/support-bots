from pathlib import Path
from typing import Any, Optional, Tuple

from aiogram.contrib.middlewares.i18n import I18nMiddleware

BASE_DIR = Path(__file__).parent.parent
LOCALE_DOMAIN = "messages"
LOCALE_DIR = BASE_DIR / "locale"

language = {}


async def set_language(user_id: int, lang: str):
    language[user_id] = lang


async def get_lang(user_id: int) -> str:
    return language.get(user_id, None)


async def get_locale_middleware(dp):
    i18n = LocaleMiddleware(LOCALE_DOMAIN, LOCALE_DIR)
    return i18n


def get_locale_middleware_sync(dp):
    i18n = LocaleMiddleware(LOCALE_DOMAIN, LOCALE_DIR)
    return i18n


class LocaleMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        user_id = args[0].from_user.id
        lang = await get_lang(user_id)
        return lang


def setup_locale_middleware(dp):
    i18n = get_locale_middleware_sync(dp)
    dp.middleware.setup(i18n)
