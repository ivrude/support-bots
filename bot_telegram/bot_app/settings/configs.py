web_ngrok = "https://387e-77-47-175-15.ngrok-free.app"

TOKEN = "6688922542:AAGh684fYzwNM1mgYdHz-iIvVYp8apOsLX0"
TOKEN_DOMAIN = "25ac8a5c-3a1d-4f05-80bf-eb23c66ff4dc"

# redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = ""


# api
url_check_number = "http://localhost:8000/api/v1/support/check_number"
url_check_email = "http://localhost:8000/api/v1/support/check_email"
url_news_list = "http://localhost:8000/api/v1/support/get_news_list"
url_get_news = "http://localhost:8000/api/v1/support/get_news"
url_new_thread = "http://localhost:8000/api/v1/support/new_thread"
url_email_code = "http://localhost:8000/api/v1/support/email_code"
headers = {"Authorization": f"Bearer {TOKEN_DOMAIN}", "Accept": "application/json"}
