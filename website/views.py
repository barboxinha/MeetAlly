from django.http import HttpResponse
from django.shortcuts import render

# View function to handle http request for welcome page
def welcome(request):
    return render(request, "website/welcome.html")


def about(request):
    return HttpResponse("MeetAlly is your one-stop shop for coordinating meetings with your peers. \r\nWe are here to be your time ally!")