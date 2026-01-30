from django.db.models import (
    Max,
    Q,
    OuterRef,
    Subquery,
    CharField,
)  # OuterRef, Subquery, CharFieldを追加

from django.db.models.functions import Coalesce, NullIf, Greatest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.list import ListView

from .forms import MessageSearchForm
from .models import Topic, Message, Reply


class IndexView(ListView):
    template_name = "main/index.html"
    model = Topic
    context_object_name = "topics"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = (
                Topic.objects.all()
                .annotate(
                    latest_message_time=Max("topic_message__created_at"),
                    # 閲覧ユーザーのメッセージについた最新の返信が作成された時間
                    latest_reply_time=Max(
                        "topic_message__created_at",
                        filter=Q(
                            topic_message__reply_from_child_message__parent_message__user=self.request.user
                        ),
                    ),
                    # 閲覧ユーザーの最新メッセージが作成された時間
                    my_latest_message_time=Max(
                        "topic_message__created_at",
                        filter=Q(topic_message__user=self.request.user),
                    ),
                    # 2 つを比較して、前者のほうが新しいときのみ取り出したい
                    # 2 つのうち最も新しいものを取り出す
                    newest=Greatest(
                        "latest_reply_time",
                        "my_latest_message_time",
                    ),
                    # 最も新しいものが後者のとき、None を返す。そうでなければ前者を返す
                    untouched_reply_time=NullIf("newest", "my_latest_message_time"),
                )
                .order_by("-untouched_reply_time", "-latest_message_time")
            )
        else:
            queryset = (
                Topic.objects.all()
                .annotate(
                    latest_message_time=Max("topic_message__created_at"),
                )
                .order_by("-latest_message_time")
            )
        return queryset


# def forum(request, topic_id):
#     topic = Topic.objects.get(id=topic_id)
#     messages = (
#         Message.objects.filter(topic=topic).order_by("created_at")
#     )
#     if request.method == "POST":
#         if request.user.is_authenticated:  # 追加
#             message = request.POST["message"]
#             Message.objects.create(
#                 topic=topic,
#                 content=message,
#                 user=request.user,  # 追加
#             )
#     context = {
#         "messages": messages,
#         "topic": topic,
#     }
#     return render(request, "main/forum.html", context)


class ForumView(ListView):
    template_name = "main/forum.html"
    context_object_name = "messages"
    paginate_by = 5

    def get_topic(self):
        return Topic.objects.get(id=self.kwargs["topic_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.get_topic()
        context["topic"] = topic

        keyword = self.request.GET.get("keyword") or ""
        context["keyword"] = keyword

        form = MessageSearchForm(self.request.GET)
        context["search_form"] = form

        parent_message_id = self.request.GET.get("parent_message_id")
        if parent_message_id:
            parent_message = Message.objects.select_related("user").get(
                id=parent_message_id
            )
        else:
            parent_message = None
        context["parent_message"] = parent_message
        return context

    def get_queryset(self, **kwargs):
        subquery_for_username = Reply.objects.filter(
            child_message=OuterRef("id")
        ).values("parent_message__user__username")
        subquery_for_content = Reply.objects.filter(
            child_message=OuterRef("id")
        ).values("parent_message__content")

        topic = self.get_topic()
        queryset = (
            Message.objects.filter(topic=topic)
            .select_related("user")
            .annotate(
                parent_message_username=Subquery(
                    subquery_for_username, output_field=CharField(), null=True
                ),
                parent_message_content=Subquery(
                    subquery_for_content, output_field=CharField(), null=True
                ),
            )
            .order_by("created_at")
        )

        keyword = self.request.GET.get("keyword")
        if keyword:
            queryset = queryset.filter(content__icontains=keyword)
        return queryset

    def post(self, request, *args, **kwargs):
        topic = self.get_topic()
        if request.user.is_authenticated:
            message = request.POST["message"]
            image = request.FILES.get("image")
            new_message = Message.objects.create(
                topic=topic,
                content=message,
                image=image,
                user=request.user,
            )
            parent_message_id = request.POST.get("parent_message_id")
            if parent_message_id:
                parent_message = Message.objects.get(id=parent_message_id)
                Reply.objects.create(
                    parent_message=parent_message, child_message=new_message
                )
        return redirect("forum", topic_id=topic.id)


def delete_message(request, topic_id, id):
    message = get_object_or_404(Message, id=id)
    message.delete()
    return redirect("forum", topic_id=topic_id)
