from django.db import models
from accounts.models import CustomUser


class Topic(models.Model):
    name = models.CharField("トピック名", max_length=20)

    def __str__(self):
        return self.name


class Message(models.Model):
    content = models.CharField("内容", max_length=200)
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="topic_message"
    )
    created_at = models.DateTimeField("投稿日時", auto_now_add=True)
    image = models.ImageField("画像", null=True, blank=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="user_message"
    )

    def __str__(self):
        return self.content


class Reply(models.Model):
    child_message = models.ForeignKey(
        Message, related_name="reply_from_child_message", on_delete=models.CASCADE
    )
    parent_message = models.ForeignKey(
        Message, related_name="reply_from_parent_message", on_delete=models.CASCADE
    )
