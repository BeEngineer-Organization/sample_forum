from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<topic_name>/", views.forum, name="forum"),
    path("<topic_name>/message/<int:pk>/delete/", views.delete_message, name="delete_message"),
]