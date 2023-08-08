from celery import Celery
from django.conf import settings
from aiogram import Bot, types
from datetime import datetime, timedelta
from .models import Responce, Event
import pymysql
import requests


app = Celery('proj', broker=settings.CELERY_BROKER_URL)
app.config_from_object('django.conf:settings')
app.conf.timezone = 'Europe/Kiev'
def get_user_ids_and_phone_numbers():
    # Connect to the database and fetch user_ids and phone_numbers from meets_client table
    connection = pymysql.connect(
        host='mysql-138752-0.cloudclusters.net',
        user='admin',
        password='CtUfEulL',
        database='themes',
        port=19653
    )
    cursor = connection.cursor()

    # Query to fetch user_ids and phone_numbers from meets_client table
    query = "SELECT user_id, phone_number FROM meets_client"
    cursor.execute(query)
    user_data = cursor.fetchall()

    connection.close()
    return user_data

# Create a Celery instance
def send_event_notifications():
    user_data = get_user_ids_and_phone_numbers()

def send_telegram_notification(user_id, message):
    # Отправить уведомление пользователю через API Telegram
    bot_token = '6542659135:AAEsVEDtZZwwazKRnTebiS3kVDr5CzTlumk'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {'chat_id': user_id, 'text': message}
    response = requests.post(url, json=data)
    return response.status_code == 200
@app.task
def send_event_notifications():
    user_data = get_user_ids_and_phone_numbers()

    # Получить текущее время и время через 24 часа
    current_time = datetime.now()
    next_day_time = current_time + timedelta(hours=24)

    connection = pymysql.connect(
        host='mysql-138752-0.cloudclusters.net',
        user='admin',
        password='CtUfEulL',
        database='themes',
        port=19653
    )
    cursor = connection.cursor()

    # Get the current time and the time after 24 hours
    current_time = datetime.now()
    next_day_time = current_time + timedelta(hours=24)

    for user_id, phone_number in user_data:
        query = "SELECT DISTINCT e.title, e.date_time FROM meets_event e INNER JOIN meets_responce r ON e.event_id = r.event_id WHERE r.phone_number = %s AND r.response = 'yes' AND e.date_time <= DATE_ADD(NOW(), INTERVAL 27 HOUR) AND e.date_time >= %s AND e.date_time <= %s"
        cursor.execute(query, (phone_number, current_time, next_day_time))
        data = cursor.fetchall()

        if data:
            response_message = "Your upcoming events:\n"
            for event_title, event_date in data:
                response_message += f"Event: {event_title}, Date: {event_date.strftime('%Y-%m-%d %H:%M')}\n"
        else:
            response_message = "You have no upcoming events in the next 24 hours."

        # Send the notification to the user
        send_telegram_notification(user_id, response_message)

    connection.close()
    return "Event notifications sent successfully."