from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:topic_id>/", views.forum, name="forum"),
    path("<int:topic_id>/message/<int:pk>/delete/", views.delete_message, name="delete_message"),
]