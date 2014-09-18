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
    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            code_list = form.code_split()
            count = len(code_list)
            print code_list
            form.code_save()
            message = str(count) + " code(s) added to " + str(form.cleaned_data['gameselect'].game)
            print message
            context = {
                'form' : CodeForm,
                'message' : message,

            }
            return render(request, 'dispenser/submit.html', context) 
        else:
            return HttpResponse('You done goofed')
    else:

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
    try:
        notes = GameCodeProfile.objects.get(id = game_id).notes
        return HttpResponse(notes)
    except:
        return HttpResponse(False)
