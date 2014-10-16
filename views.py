from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required

from dispenser.models import GameCodeProfile, Code, CodeForm, GameSelectForm, GetCodeForm, GetWinnerForm
# Create your views here.

#@permission_required('dispenser.can_access')
def main_page(request):
    youtube = 'dmVWvOC_2HU'
    context = {
        'youtube': youtube,
    }
    return render(request, 'dispenser/main.html', context)

@permission_required('dispenser.can_access')
def submit(request):
    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            code_list = form.code_split()
            print code_list
            invalid = form.code_save()
            count = len(code_list) - len(invalid)
            message = str(count) + " code(s) added to " + str(form.cleaned_data['gameselect'].game)
            print message
            
            context = {
                'form' : CodeForm,
                'message' : message,
                'invalid' : invalid,

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
    if request.method == 'POST':
        gsf = GameSelectForm(request.POST)
        if not gsf.is_valid():
            return HttpResponse('I don\'t know how you messed that up, but you did. Nice going.')
        else:
            url = '/dispenser/retrieve/get/' + str(gsf.cleaned_data['gameselect'].id)
            print url
            return redirect(url)
    else:
        game_select = GameSelectForm
        context = {
            'form' : '/dispenser/retrieve/',
            'game_select' : game_select,
        }
        return render(request, 'dispenser/retrieve.html', context)

@permission_required('dispenser.can_access')
def retrieve_code(request, game_id):
    game_profile = get_object_or_404(GameCodeProfile.objects.filter(id = game_id))
    game_name = game_profile
    code = game_profile.get_code()
    if not code:
        return HttpResponse('No more codes for this game!')
    get_code = GetCodeForm(initial = {'code':code.code})
    if request.method == 'POST':
        if 'form_cancel' in request.POST:
            print 'form cancel'
            return redirect('/dispenser/retrieve')
        processing_code = GetCodeForm(request.POST)
        if not processing_code.is_valid():
            return HttpResponse('You forgot to give this code to someone.')
        print processing_code.cleaned_data
        
        if 'form_commit' in request.POST:
            print 'form commit'
            _process_code(**processing_code.cleaned_data)
            game_profile.update_count()
            return redirect('/dispenser/retrieve')
        elif 'form_again' in request.POST:
            print 'form again'   
            _process_code(**processing_code.cleaned_data)
            game_profile.update_count()
            url =  '/dispenser/retrieve/get/' + str(game_id)
            return redirect(url)
        else:
            return HttpResponse('what')
    context = {
        'game_note' : GameCodeProfile.objects.get(id = game_id).notes,
        'game_name' : game_name,
        'get_code' : get_code,
        'game_id' : game_id,
    }
    return render(request, 'dispenser/code.html', context)

#batch listing
@permission_required('dispenser.can_access')
def batch(request):
    if request.method == 'POST':
        gsf = GameSelectForm(request.POST)
        if not gsf.is_valid():
            return HttpResponse('I don\'t know how you messed that up, but you did. Nice going.')
        else:
            url = '/dispenser/batch/get/' + str(gsf.cleaned_data['gameselect'].id)
            print url
            return redirect(url)
    else:
        game_select = GameSelectForm
        context = {
            'form' : '/dispenser/batch/',
            'game_select' : game_select,
        }
        return render(request, 'dispenser/retrieve.html', context)

@permission_required('dispenser.can_access')
def batch_code(request, game_id):
    game_profile = get_object_or_404(GameCodeProfile.objects.filter(id = game_id))
    game_name = game_profile
    code = game_profile.get_all_codes()
    if not code:
        return HttpResponse('No codes for this game!')
    get_code = []
    for entry in code:
        get_code.append(GetCodeForm(initial = {'code':entry.code, 'assigned':entry.assigned, 'used':entry.used}))
    if request.method == 'POST':
        if 'form_cancel' in request.POST:
            print 'form cancel'
            return redirect('/dispenser/batch')
        processing_code = GetCodeForm(request.POST)
        if not processing_code.is_valid():
            return HttpResponse('You done goofed.')
        print processing_code.cleaned_data
        
        if 'form_commit' in request.POST:
            print 'form commit'
            _process_code(**processing_code.cleaned_data)
            game_profile.update_count()
            return redirect('/dispenser/batch')
        elif 'form_again' in request.POST:
            print 'form again'   
            _process_code(**processing_code.cleaned_data)
            game_profile.update_count()
            url =  '/dispenser/batch/get/' + str(game_id)
            return redirect(url)
        else:
            return HttpResponse('what')
    context = {
        'game_note' : GameCodeProfile.objects.get(id = game_id).notes,
        'game_name' : game_name,
        'get_code' : get_code,
        'game_id' : game_id,
    }
    return render(request, 'dispenser/batch.html', context)

def find(request):
    if request.method == 'POST':
        get_form = GetWinnerForm(request.POST)
        if get_form.is_valid():
            result = get_form.get_winner() 
            context = {
                'form' : get_form,
                'result' : result,
            }
        else:
            return HttpResponse('You done goofed.')
    else:
        get_form = GetWinnerForm()
        result = ''
        context = {
            'form' : get_form,
            'result' : result,
        }
    return render(request, 'dispenser/find.html',context)

def _process_code(assigned, code, used):
    code = Code.objects.get(code = code)
    code.assigned = assigned
    code.used = used
    code.save()


def get_notes(request, game_id):
    try:
        notes = GameCodeProfile.objects.get(id = game_id).notes
        return HttpResponse(notes)
    except:
        return HttpResponse(False)
