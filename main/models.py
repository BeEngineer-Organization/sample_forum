from django.db import models
from accounts.models import CustomUser

class Topic(models.Model):
    name = models.CharField("トピック名", max_length=20)

    def __str__(self):
        return self.name


class Message(models.Model):
    content = models.CharField("内容", max_length=200)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="topic_message")
    created_at = models.DateTimeField("投稿日時", auto_now_add=True)
    image = models.ImageField("画像", null=True, blank=True) # 追加
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_message") # 追加

    def __str__(self):
        return self.content
