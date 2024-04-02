from django.http import HttpResponse
from django.shortcuts import render

# View function to handle http request for welcome page
def welcome(request):
    return HttpResponse("Welcome to MeetAlly! Glad to see you here!")


def about(request):
    return HttpResponse("MeetAlly is your one-stop shop for coordinating meetings with your peers. \r\nWe are here to be your time ally!")