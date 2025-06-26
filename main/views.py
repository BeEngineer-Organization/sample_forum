from django.shortcuts import get_object_or_404, redirect, render

from .models import Topic, Message


def index(request):
    TOPIC_LIST = Topic.objects.all()
    context = {
        "topics": TOPIC_LIST,
    }
    return render(request, "main/index.html", context)


def forum(request, topic):
    topic = Topic.objects.get(name=topic)
    messages = Message.objects.filter(topic=topic).order_by("created_at")
    try:
        message = request.POST["message"]
        Message.objects.create(
            topic=topic,
            content=message,
        )
    except:
        pass
    return render(request, "main/forum.html", {"messages": messages, "topic": topic})


def delete_message(request, topic, pk):
    message = get_object_or_404(Message, pk=pk)
    if request.method == "POST":
        message.delete()
    return redirect("forum", topic=topic)