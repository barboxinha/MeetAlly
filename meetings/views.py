from django.shortcuts import redirect, render, get_object_or_404
from django.forms import modelform_factory
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from meetings.models import Meeting, Room


def can_manage(user, meeting):
    # Only a meeting's participants (and superusers) may change or delete it
    return user.is_superuser or meeting.participants.filter(pk=user.pk).exists()


# View functions
@login_required
def detail(request, id):
    meeting = get_object_or_404(Meeting, pk=id)
    context = {"meeting": meeting, "can_manage": can_manage(request.user, meeting)}
    return render(request, "meetings/detail.html", context)


@login_required
def room_list(request):
    rooms = Room.objects.all()
    return render(request, "meetings/room_list.html", {"rooms": rooms})


RoomForm = modelform_factory(Room, exclude=[])

@login_required
def new_room(request):
    # Only superusers can add rooms; the button is hidden for everyone else,
    # but the URL could still be typed in directly.
    if not request.user.is_superuser:
        raise PermissionDenied
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("rooms")
    else:
        form = RoomForm()
    return render(request, "meetings/new_room.html", {"form": form})


# This is a new class generated from your model by the modelform_factory function.
# To exclude specific fields from the form, pass them as a list to the exclude parameter.
MeetingForm = modelform_factory(Meeting, exclude=[])

@login_required
def new(request):
    if request.method == "POST":
        form = MeetingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("welcome")
    else:
        form = MeetingForm()  
    return render(request, "meetings/new.html", {"form": form})


@login_required
def edit(request, id):
    meeting = get_object_or_404(Meeting, pk=id)
    if not can_manage(request.user, meeting):
        raise PermissionDenied
    if request.method == "POST":
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            return redirect("detail", id)
    else:
        form = MeetingForm(instance=meeting)
    return render(request, "meetings/edit.html", {"form": form})


@login_required
def delete(request, id):
    meeting = get_object_or_404(Meeting, pk=id)
    if not can_manage(request.user, meeting):
        raise PermissionDenied
    if request.method == "POST":
        # Form is only shown to ask for confirmation.
        # When we get a POST request, we know we can go ahead and delete.
        meeting.delete()
        return redirect("welcome")
    return render(request, "meetings/confirm_delete.html", {"meeting": meeting})