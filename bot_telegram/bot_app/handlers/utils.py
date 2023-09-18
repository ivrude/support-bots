from aiogram.dispatcher.filters.state import State, StatesGroup

from ..app import dp
from ..settings.locale import get_locale_middleware_sync, setup_locale_middleware

setup_locale_middleware(dp)


class YourState(StatesGroup):
    waiting_for_contact = State()
    waiting_for_email = State()
    waiting_for_code = State()
    settings = State()
    menu = State()
    offers = State()
    main = State()
    feedback = State()
    waiting_for_wish = State()
    waiting_for_complain = State()
    waiting_for_language = State()
    waiting_for_issue = State()


i18n = get_locale_middleware_sync(dp)
_ = i18n.gettext
