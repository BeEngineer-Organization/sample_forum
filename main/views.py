from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.list import ListView

from .forms import MessageSearchForm
from .models import Topic, Message


class IndexView(ListView):
    template_name = "main/index.html"
    model = Topic
    context_object_name = "topics"

    def get_queryset(self, **kwargs):
        queryset = (
            Topic.objects.all()
        )
        return queryset


# def forum(request, topic_name):
#     topic = Topic.objects.get(name=topic_name)
#     messages = (
#         Message.objects.filter(topic=topic).order_by("created_at")
#     )
#     if request.method == "POST":
#         if request.user.is_authenticated:  # 追加
#             message = request.POST["message"]
#             Message.objects.create(
#                 topic=topic,
#                 content=message,
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
        return Topic.objects.get(name=self.kwargs["topic_name"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.get_topic()
        context["topic"] = topic

        form = MessageSearchForm(self.request.GET)
        if form.is_valid():
            context["keyword"] = form.cleaned_data["keyword"]

        context["search_form"] = form
        return context

    def get_queryset(self, **kwargs):
        topic = self.get_topic()
        queryset = Message.objects.filter(topic=topic).order_by("created_at")

        form = MessageSearchForm(self.request.GET)
        if form.is_valid():
            keyword = form.cleaned_data["keyword"]
            if keyword:
                queryset = queryset.filter(content__icontains=keyword)
        return queryset

    def post(self, request, *args, **kwargs):
        topic = self.get_topic()
        if request.user.is_authenticated:
            message = request.POST["message"]
            image = request.FILES.get("image")
            Message.objects.create(
                topic=topic,
                content=message,
                image=image,
                user=request.user,
            )
        return redirect("forum", topic_name=topic.name)


def delete_message(request, topic_name, pk):
    message = get_object_or_404(Message, pk=pk)
    message.delete()
    return redirect("forum", topic_name=topic_name)