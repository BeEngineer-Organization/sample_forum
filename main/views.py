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
            # queryset = Topic.objects.all().annotate(
            #     topic_message__created_at__max=Max(
            #         "topic_message__created_at"
            #     ),
            #     my_topic_message__created_at__max=Max(
            #         "topic_message__created_at",
            #         filter=Q(topic_message__user=self.request.user),
            #     ),
            #     for_comparison=Coalesce(
            #         "my_topic_message__created_at__max", "topic_message__created_at__max"
            #     ),
            #     others_topic_message__created_at__max=NullIf(
            #         "topic_message__created_at__max", "for_comparison"
            #     ),
            # ).order_by("-others_topic_message__created_at__max", "-topic_message__created_at__max")

            my_topic_message_with_reply = Message.objects.filter(
                user=self.request.user, reply_from_parent_message__isnull=False
            )
            for t in my_topic_message_with_reply:
                print(t.created_at)

            queryset = (
                Topic.objects.all()
                .annotate(
                    topic_message__created_at__max=Max("topic_message__created_at"),
                    # 閲覧ユーザーのメッセージについた最新の返信が作成された時間
                    topic_message_with_my_parent_reply__created_at__max=Max(
                        "topic_message__created_at",
                        filter=Q(
                            topic_message__reply_from_child_message__parent_message__user=self.request.user
                        ),
                    ),
                    # 閲覧ユーザーの最新メッセージが作成された時間
                    my_topic_message__created_at__max=Max(
                        "topic_message__created_at",
                        filter=Q(topic_message__user=self.request.user),
                    ),
                    # 閲覧ユーザーのメッセージについた最新の返信と閲覧ユーザーの最新メッセージで新しいほう
                    newest=Greatest(
                        "topic_message_with_my_parent_reply__created_at__max",
                        "my_topic_message__created_at__max",
                    ),
                    # 新しいほうが閲覧ユーザーのメッセージについた最新の返信である場合、それを返す。そうでなければ None を返す
                    latest_reply_time=NullIf(
                        "newest", "my_topic_message__created_at__max"
                    ),
                )
                .order_by("-latest_reply_time", "-topic_message__created_at__max")
            )
        else:
            queryset = (
                Topic.objects.all()
                .annotate(
                    topic_message__created_at__max=Max("topic_message__created_at"),
                )
                .order_by("-topic_message__created_at__max")
            )
        return queryset


# def forum(request, topic_id):
#     topic = Topic.objects.get(pk=topic_id)
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
        return Topic.objects.get(pk=self.kwargs["topic_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.get_topic()
        context["topic"] = topic

        keyword = self.request.GET.get("keyword") or ""
        context["keyword"] = keyword

        form = MessageSearchForm(self.request.GET)
        context["search_form"] = form

        parent_message_pk = self.request.GET.get("parent_message_pk")
        if parent_message_pk:
            parent_message = Message.objects.select_related("user").get(
                pk=parent_message_pk
            )
        else:
            parent_message = None
        context["parent_message"] = parent_message
        return context

    def get_queryset(self, **kwargs):
        subquery_for_username = Reply.objects.filter(
            child_message=OuterRef("pk")
        ).values("parent_message__user__username")
        subquery_for_content = Reply.objects.filter(
            child_message=OuterRef("pk")
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
            parent_message_pk = request.POST.get("parent_message_pk")
            if parent_message_pk:
                parent_message = Message.objects.get(pk=parent_message_pk)
                Reply.objects.create(
                    parent_message=parent_message, child_message=new_message
                )
        return redirect("forum", topic_id=topic.pk)


def delete_message(request, topic_id, pk):
    message = get_object_or_404(Message, pk=pk)
    message.delete()
    return redirect("forum", topic_id=topic_id)
