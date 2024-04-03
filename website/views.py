from django.http import HttpResponse
from django.shortcuts import render

from meetings.models import Meeting

# View functions to handle http requests
def welcome(request):
    return render(request, template_name="website/welcome.html", context={"num_meetings": Meeting.objects.count()})


def about(request):
    return HttpResponse("MeetAlly is your one-stop shop for coordinating meetings with your peers. \r\nWe are here to be your time ally!")