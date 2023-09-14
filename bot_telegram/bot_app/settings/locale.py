from pathlib import Path
from typing import Any, Optional, Tuple

from aiogram.contrib.middlewares.i18n import I18nMiddleware

from ..app import storage

BASE_DIR = Path(__file__).parent.parent
LOCALE_DOMAIN = "messages"
LOCALE_DIR = BASE_DIR / "locale"


async def get_locale_middleware(dp):
    i18n = LocaleMiddleware(LOCALE_DOMAIN, LOCALE_DIR)
    return i18n


def get_locale_middleware_sync(dp):
    i18n = LocaleMiddleware(LOCALE_DOMAIN, LOCALE_DIR)
    return i18n


class LocaleMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        user_id = args[0].from_user.id
        stored_data = await storage.get_data(chat=user_id, user=user_id)
        if "language" in stored_data:

            selected_language = stored_data["language"]
        else:
            selected_language = "en"
        return selected_language


def setup_locale_middleware(dp):
    i18n = get_locale_middleware_sync(dp)
    dp.middleware.setup(i18n)
