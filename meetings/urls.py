"""
URLs for the meetings app.
"""
from django.urls import path

from meetings import views

urlpatterns = [
    path('<int:id>', views.detail, name="detail"),
    path('rooms', views.room_list, name="rooms"),
    path('rooms/new', views.new_room, name="new_room"),
    path('new', views.new, name="new"),
    path('edit/<int:id>', views.edit, name="edit"),
    path('delete/<int:id>', views.delete, name="delete")
]