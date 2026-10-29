from django.contrib import admin
from django.contrib.admin import ModelAdmin

from meetings.models import Meeting, Room


admin.site.register(Room)

# Customize the admin interface
@admin.register(Meeting)
class MeetingAdmin(ModelAdmin):
    model = Meeting
    list_display = ['id', 'title', 'date', 'start_time', 'room']
    ordering = ('date', 'start_time')
    search_fields = ('title', 'date')