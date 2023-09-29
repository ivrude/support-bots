import logging

from . import commands
from .app import TOKEN, app, bot, dp, webhook_path

logging.basicConfig(level=logging.INFO)
