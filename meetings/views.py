from django.shortcuts import render, get_object_or_404

from meetings.models import Meeting, Room

# View function for detail of a meeting
def detail(request, id):
    meeting = get_object_or_404(Meeting, pk=id)
    return render(request, "meetings/detail.html", {"meeting": meeting})

def room_list(request):
    rooms = Room.objects.all()
    return render(request, "meetings/room_list.html", {"rooms": rooms})