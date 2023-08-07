
from .models import *
from .serialize import ThemeSerializer
from rest_framework import serializers

from rest_framework.views import APIView
from rest_framework.response import Response


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = '__all__'
class EventSerializer(serializers.ModelSerializer):
    theme = ThemeSerializer()  # Використання ThemeSerializer для поля theme

    class Meta:
        model = Event
        fields = '__all__'

class AllThemes(APIView):
    def get(self, request, *args, **kwargs):
        all_themes = Theme.objects.all()
        serialized_theme = ThemeSerializer(all_themes, many=True)
        return Response(serialized_theme.data)
class AllEvents(APIView):
    def get(self, *args, **kwargs):
        all_events = Event.objects.all()
        serialized_event = EventSerializer(all_events, many=True)
        return Response(serialized_event.data)
