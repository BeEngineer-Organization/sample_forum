from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:topic_id>/", views.ForumView.as_view(), name="forum"),
    path(
        "<int:topic_id>/message/<int:pk>/delete/",
        views.delete_message,
        name="delete_message",
    ),
]
