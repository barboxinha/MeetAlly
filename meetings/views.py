from django.shortcuts import redirect, render, get_object_or_404
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
    if request.method == "POST":
        form = MeetingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("welcome")
    else:
        form = MeetingForm()  
    return render(request, "meetings/new.html", {"form": form})


def edit(request, id):
    meeting = get_object_or_404(Meeting, pk=id)
    if request.method == "POST":
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            return redirect("detail", id)
    else:
        form = MeetingForm(instance=meeting)
    return render(request, "meetings/edit.html", {"form": form})