from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required

from dispenser.models import GameCodeProfile, Code, CodeForm
# Create your views here.

@permission_required('dispenser.can_access')
def main_page(request):
    context = {

    }
    return render(request, 'dispenser/main.html', context)

@permission_required('dispenser.can_access')
def submit(request):
    context = {
    'form' : CodeForm,
    }
    
    return render(request, 'dispenser/submit.html', context)

@permission_required('dispenser.can_access')
def retrieve(request):
    context = {

    }
    return render(request, 'dispenser/retrieve.html', context)
def get_notes(request, game_id):
    return HttpResponse(game_id)
