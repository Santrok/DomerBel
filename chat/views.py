from django.shortcuts import render, redirect


# Create your views here.


def chat_page(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("home")
    context = {}
    return render(request, "chat.html", context)