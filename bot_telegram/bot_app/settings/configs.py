import os

web_ngrok = "https://c911-85-114-213-169.ngrok.io"

TOKEN = "6059087374:AAEg4bLEIJqF-PFkjwfIDeOSbESRrJsvvLs"
TOKEN_DOMAIN = "72c513f9-d8f7-42ef-8e55-528bf3eef117"

# redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = ""


# api
BASE_HOST = "http://localhost:8880"
url_check_number = BASE_HOST + "/api/v1/support/check_number"
url_check_email = BASE_HOST + "/api/v1/support/check_email"
url_news_list = BASE_HOST + "/api/v1/support/get_news_list"
url_get_news = BASE_HOST + "/api/v1/support/get_news"
url_new_thread = BASE_HOST + "/api/v1/support/new_thread"
url_email_code = BASE_HOST + "/api/v1/support/email_code"
url_check_email_code = BASE_HOST + "/api/v1/support/check_email_code"
url_send_photo = BASE_HOST + "/api/v1/support/send_photo"
url_send_video = BASE_HOST + "/api/v1/support/send_video"



headers = {"Authorization": f"Bearer {TOKEN_DOMAIN}", "Accept": "application/json"}
