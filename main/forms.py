from django import forms

from .models import Message


class MessageSearchForm(forms.Form):
    keyword = forms.CharField(
        label="検索",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "投稿を検索"}),
    )


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content", "image"]
        widgets = {
            "content": forms.TextInput(
                attrs={
                    "class": "message-input",
                    "placeholder": "メッセージを入力",
                }
            ),
        }
