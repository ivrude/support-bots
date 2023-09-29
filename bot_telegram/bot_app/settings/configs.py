import os

web_ngrok = os.environ.get("NGROK_URL")

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TOKEN_DOMAIN = os.environ.get("DOMAIN_TOKEN")

# redis
REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = ""


# api
BASE_HOST = "http://host.docker.internal:8000"
url_check_number = BASE_HOST + "/api/v1/support/check_number"
url_check_email = BASE_HOST + "/api/v1/support/check_email"
url_news_list = BASE_HOST + "/api/v1/support/get_news_list"
url_get_news = BASE_HOST + "/api/v1/support/get_news"
url_new_thread = BASE_HOST + "/api/v1/support/new_thread"
url_email_code = BASE_HOST + "/api/v1/support/email_code"
url_check_email_code = BASE_HOST + "/api/v1/support/check_email_code"


headers = {"DOMAIN-UUID": TOKEN_DOMAIN, "Accept": "application/json"}
