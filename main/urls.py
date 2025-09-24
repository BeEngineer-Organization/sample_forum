from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<topic_name>/", views.ForumView.as_view(), name="forum"),
    path("<topic_name>/message/<int:pk>/delete/", views.delete_message, name="delete_message"),
]