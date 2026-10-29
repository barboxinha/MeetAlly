from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render

from meetings.models import Meeting

# View functions to handle http requests
def welcome(request):
    if request.user.is_authenticated:
        context = {"meetings": Meeting.objects.all()}
    else:
        context = {}
    return render(request, template_name="website/welcome.html", context=context)


def signup(request):
    if request.user.is_authenticated:
        return redirect("welcome")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Log the new user straight in rather than sending them to the login page
            login(request, form.save())
            return redirect("welcome")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def about(request):
    return HttpResponse("MeetAlly is your one-stop shop for coordinating meetings with your peers. \r\nWe are here to be your time ally!")