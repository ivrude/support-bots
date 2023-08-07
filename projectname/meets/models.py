from django.db import models
from django.utils import timezone
from datetime import timedelta


# Модель теми (theme)
class Theme(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

# Модель заходу (event)
class Event(models.Model):
    theme_id = models.ForeignKey(Theme, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_time = models.DateTimeField()

    def __str__(self):
        return self.title

# Модель клієнта (client)
class Client(models.Model):
    user_id = models.IntegerField(unique=True)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return str(self.user_id)

# Модель відповіді на захід (response)
class Responce(models.Model):
    RESPONSE_CHOICES = (
        ('yes', 'Записатись'),
        ('maybe', 'Можливо буду'),
        ('no', 'Не прийду')
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    response = models.CharField(max_length=10, choices=RESPONSE_CHOICES)

    def __str__(self):
        return f"{self.client} - {self.get_response_display()} - {self.event}"
