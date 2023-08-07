from django.urls import path
from .views import *
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('themes/', AllThemes.as_view(), name='all-themes'),
    path('events/', AllEvents.as_view(), name='all-events'),
]