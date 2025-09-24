from django import forms

class MessageSearchForm(forms.Form):
    keyword = forms.CharField(
        label="検索",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "投稿を検索"}),
    )
