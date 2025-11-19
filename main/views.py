from django.shortcuts import get_object_or_404, redirect, render

from .models import Topic, Message


def index(request):
    TOPIC_LIST = Topic.objects.all()
    context = {
        "topics": TOPIC_LIST,
    }
    return render(request, "main/index.html", context)


def forum(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    print(topic)
    messages = Message.objects.filter(topic=topic).order_by("created_at")
    if request.method == "POST":
        message = request.POST["message"]
        Message.objects.create(
            topic=topic,
            content=message,
        )
    context = {
        "messages": messages,
        "topic": topic
    }
    return render(request, "main/forum.html", context)


def delete_message(request, topic_id, pk):
    message = get_object_or_404(Message, pk=pk)
    message.delete()
    return redirect("forum", topic_id=topic_id)