from celery import Celery
from django.conf import settings
from aiogram import Bot, types
from datetime import datetime, timedelta
from .models import Responce, Event
import pymysql
import requests


app = Celery('proj', broker=settings.CELERY_BROKER_URL)
app.config_from_object('django.conf:settings')
def get_user_ids_from_meets_client():
    # Connect to the database and fetch all user_ids from the meets_client table
    connection = pymysql.connect(
        host='mysql-138752-0.cloudclusters.net',
        user='admin',
        password='CtUfEulL',
        database='themes',
        port=19653
    )
    cursor = connection.cursor()

    # Query to fetch all user_ids from the meets_client table
    query = "SELECT DISTINCT user_id FROM meets_client"
    cursor.execute(query)
    user_ids = [row[0] for row in cursor.fetchall()]

    connection.close()
    return user_ids

def get_phone_number_from_database(user_id):
    # Retrieve the user's phone number from the 'meets_client' table
    connection = pymysql.connect(
        host='mysql-138752-0.cloudclusters.net',
        user='admin',
        password='CtUfEulL',
        database='themes',
        port=19653
    )
    cursor = connection.cursor()

    query = "SELECT phone_number FROM meets_client WHERE user_id=%s"
    cursor.execute(query, (user_id,))
    data = cursor.fetchone()
    connection.close()

    if data:
        return data[0]  # Return the phone number from the database
    else:
        return None

def send_telegram_notification(user_id, message):
    # Send mmessage by API
    bot_token = '6542659135:AAEsVEDtZZwwazKRnTebiS3kVDr5CzTlumk'  
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {'chat_id': user_id, 'text': message}
    response = requests.post(url, json=data)
    return response.status_code == 200
@app.task
def send_event_notifications():
    user_ids = get_user_ids_from_meets_client()

    current_time = datetime.now()
    next_day_time = current_time + timedelta(hours=24)

    for user_id in user_ids:
        phone_number = get_phone_number_from_database(user_id)
        if phone_number:
            connection = pymysql.connect(
                host='mysql-138752-0.cloudclusters.net',
                user='admin',
                password='CtUfEulL',
                database='themes',
                port=19653
            )
            cursor = connection.cursor()
            query = "SELECT DISTINCT e.title, e.date_time FROM meets_event e INNER JOIN meets_responce r ON e.event_id = r.event_id WHERE r.phone_number = %s AND e.date_time <= DATE_ADD(NOW(), INTERVAL 1 DAY) AND e.date_time >= %s AND e.date_time <= %s"
            cursor.execute(query, (phone_number, current_time, next_day_time))
            data = cursor.fetchall()
            connection.close()

            if data:
                response_message = "Your upcoming events:\n"
                for event_title, event_date in data:
                    response_message += f"Event: {event_title}, Date: {event_date.strftime('%Y-%m-%d %H:%M')}\n"
            else:
                response_message = "You have no upcoming events in the next 24 hours."

            # Sending message using API
            send_telegram_notification(user_id, response_message)
    return "Event notifications sent successfully."
