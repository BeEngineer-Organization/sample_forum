from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView

from .forms import MessageSearchForm, ReplyForm
from .models import Topic, Message


class IndexView(ListView):
    template_name = "main/index.html"
    model = Topic
    context_object_name = "topics"


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
        return Topic.objects.get(name=self.kwargs["topic_name"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.get_topic()
        context["topic"] = topic

        keyword = self.request.GET.get("keyword") or ""
        context["keyword"] = keyword

        form = MessageSearchForm(self.request.GET)
        context["search_form"] = form
        return context

    def get_queryset(self, **kwargs):
        topic = self.get_topic()
        queryset = Message.objects.filter(topic=topic).order_by("created_at")

        keyword = self.request.GET.get("keyword")
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


class ReplyView(LoginRequiredMixin, CreateView):
    template_name = "main/reply.html"
    model = Message
    form_class = ReplyForm

    def get_topic(self):
        return Topic.objects.get(name=self.kwargs["topic_name"])

    def get_message(self):
        return Message.objects.get(pk=self.kwargs["pk"])

    def get_success_url(self):
        topic = self.get_topic()
        return reverse_lazy("forum", kwargs={"topic_name": topic.name})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.get_topic()
        context["topic"] = topic
        message = self.get_message()
        context["message"] = message
        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        topic = self.get_topic()
        object.topic = topic
        object.save()

        # オブジェクト作成後にreply_toに追加
        message = self.get_message()
        object.reply_to.add(message)
        return super().form_valid(form)
