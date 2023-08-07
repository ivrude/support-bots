from django.contrib import admin
from .models import Theme, Event, Client, Responce
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name',)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title','description','date_time','theme_id')
class ClientAdmin(admin.ModelAdmin):
    list_display = ('phone_number',)
class ResponceAdmin(admin.ModelAdmin):
    list_display = ('client','response','event_id',)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Responce, ResponceAdmin)