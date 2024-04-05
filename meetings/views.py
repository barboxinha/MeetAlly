from django.shortcuts import render, get_object_or_404
from django.forms import modelform_factory

from meetings.models import Meeting, Room


# View functions
def detail(request, id):
    meeting = get_object_or_404(Meeting, pk=id)
    return render(request, "meetings/detail.html", {"meeting": meeting})


def room_list(request):
    rooms = Room.objects.all()
    return render(request, "meetings/room_list.html", {"rooms": rooms})


# This is a new class generated from your model by the modelform_factory function.
# To exclude specific fields from the form, pass them as a list to the exclude parameter.
MeetingForm = modelform_factory(Meeting, exclude=[])

def new(request):
    form = MeetingForm()
    return render(request, "meetings/new.html", {"form": form})