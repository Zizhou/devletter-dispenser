from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required

from dispenser.models import GameCodeProfile, Code, CodeForm, GameSelectForm, GetCodeForm, GetWinnerForm, Settings

#so much for loose coupling...(not that any of the devletter modules are)
from display.models import UserProfile

import random, mailbot

from auto_code import AutoCode

#TODO
DONATION_GIVEAWAY_ID = Settings.objects.all()[0].donation_id

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
        game_profile.update_count()
        return HttpResponse('No more codes for this game!')
    get_code = GetCodeForm(initial = {'code':code.code,'used':True,'codepocalypse':False})
    if request.method == 'POST':
        if 'form_cancel' in request.POST:
            print 'form cancel'
            return redirect('/dispenser/retrieve')
        processing_code = GetCodeForm(request.POST)
        if not processing_code.is_valid():
            print request.POST 
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
        game_profile.update_count()
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

@permission_required('dispenser.can_access')
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

@permission_required('dispenser.can_access')
def rand(request):
    try:
        game_profile = GameCodeProfile.objects.exclude(count = 0).order_by('?')[0]
    except:
        return HttpResponse('something went wrong')

    game_id = game_profile.id
    game_name = game_profile
    code = game_profile.get_code()
    if not code:
        return HttpResponse('no more codes')
    get_code = GetCodeForm(initial = {'code':code.code, 'used':True,'codepocalypse':True})
    if request.method == 'POST':
        print request.POST
        if 'form_cancel' in request.POST:
            print 'form cancel'
            return redirect('/dispenser/codepocalypse/')
        processing_code = GetCodeForm(request.POST)
        if not processing_code.is_valid():
            return HttpResponse('You forgot to give this code to someone.')
        print processing_code.cleaned_data
        
        if 'form_commit' in request.POST:
            print 'form commit'
            _process_code(**processing_code.cleaned_data)
            game_profile.update_count()
            return redirect('/dispenser/codepocalypse/')
        elif 'form_again' in request.POST:
            print 'form again'   
            _process_code(**processing_code.cleaned_data)
            game_profile.update_count()
            url =  '/dispenser/codepocalypse/'
            return redirect(url)
        else:
            return HttpResponse('what')
    context = {
        'game_note' : GameCodeProfile.objects.get(id = game_id).notes,
        'game_name' : game_name,
        'get_code' : get_code,
        'game_id' : game_id,
    }
    return render(request, 'dispenser/codepocalypse.html', context)

def bulk_export(request):
    if request.method == 'POST':
        form = GameSelectForm(request.POST)
        if form.is_valid():
            game = form.cleaned_data['gameselect']
            exported = []
            for x in game.code_set.filter(used = False):
                exported.append(x.code)
                x.uuid_assign('codenarok-' + unicode(x.game))
            game.update_count()
            context = {
                'form' : form,
                'game' : game,
                'exported' : exported,
            }

            return render(request, 'dispenser/export.html', context)

    form = GameSelectForm()
    
    context = {
        'form' : form,
    }


    return render(request, 'dispenser/export.html', context)


##Automatic distribution experiment
#and here I thought I was done...

@permission_required('dispenser.can_access')
def auto_main(request):
    profile = UserProfile.objects.get(user = request.user)
    context = {
        'ticket_form' : GameSelectForm(),
        'ticket_count': profile.ticket_count,

    }
    return render(request, 'dispenser/auto_main.html', context)

#donation simulator
@permission_required('dispenser.can_access')
def auto_donate(request):
    #you thought you were going to break things by not having an e-mail? ha!
    if not request.user.email:
        return redirect('account/email')
    if request.method == 'POST':

#TODO: game selection not necessarily hardcoded
        game_id = DONATION_GIVEAWAY_ID 
#TODO: donation message based on real donation info
#I don't actually have systems for that. This isn't a real marathon site!
        donation = 'Thank you for your donation of ' + str(random.randint(2,100)) + ' ' + random.choice(['US Dollars', 'Bahraini Dinars', 'Icelandic Krona', 'Pakistani Rupees', 'Qatari Rial','Tanzanian Shillings','South Korean Won','Colombian Pesos','Estonian Kroon']) +'.'
        game = AutoCode()
        print game
        attach_code = game.code_select(request.user.email, game_id)
        subject = 'Thank you for "donating"'
        if attach_code:
            url_get = game.get_url_get()
            url_return = game.get_url_return()
        #hahaha, oh wow what is this mess
            message = donation + '<br>' + 'Here is a code for ' + str(game.game) +'.<br> To redeem it, go to '+url_get+'<br>If you would like to return it to us, go to '+url_return + '<br>This link will expire in 7 days, so don\'t forget to redeem it!'
        else:
            message = donation + '<br>Unfortunately, we are out of codes for '+str(game.game) + '.' 
        print message
        donation_mail = mailbot.pack_MIME(message, request.user.email, subject)
        mailbot.send_mail(donation_mail, request.user.email)
        
        update_ticket = UserProfile.objects.get(user = request.user)
        update_ticket.ticket_increment(1)
        if update_ticket.donation_update():
            print 'yes'
        context = {
            'donation': donation,
            'game' : game.game,
            
        }
        return render(request, 'dispenser/auto_donate.html', context)
    else:
        return redirect('/dispenser/auto')

def auto_ticket(request):
    #you thought you were going to break things by not having an e-mail? ha!
    if not request.user.email:
        return redirect('account/email')
    if request.method == 'POST':
        game = AutoCode()
        #!!!
        #let's talk about security sometime...(...later)(...never)
        up = UserProfile.objects.get(user = request.user)
        if 'ticket_random' in request.POST:
            if up.ticket_decrement(1):
                if not game.code_rand(request.user.email):
#this wouldn't be necessary if I didn't do these 'function evaluates t/f' things
                    up.ticket_increment(1) 
                    return HttpResponse('Oops<br>You have been refunded.')
            else:
                return HttpResponse('not enough tickets: '+str(up.ticket_count))
        elif 'ticket_selection' in request.POST:
            gsf = GameSelectForm(request.POST)
            if gsf.is_valid():
                if up.ticket_decrement(2):
                    if not game.code_select(request.user.email, gsf.cleaned_data['gameselect'].id):
                        up.ticket_increment(2)
                        return HttpResponse('Oops<br>You have been refunded.')
                else:
                    return HttpResponse('not enough tickets: '+str(up.ticket_count))
            else:
                return HttpResponse('invalid choice')
            
#TODO
        print game
        print str(game.code)
        attach_code = game
        subject = 'Here is your requested code!'
        if attach_code:
            url_get = game.get_url_get()
            url_return = game.get_url_return()
        #hahaha, oh wow what is this mess
            message = '<br>' + 'Here is a code for ' + str(game.game) +'.<br> To redeem it, go to '+url_get+'<br>If you would like to return it to us, go to '+url_return
        else:
            message = '<br>Unfortunately, we are out of codes for '+str(game.game) + '.' 
        print message
        donation_mail = mailbot.pack_MIME(message, request.user.email, subject)
        mailbot.send_mail(donation_mail, request.user.email)
        
   
        diagnostic = str(game.game.id)
        return HttpResponse('Check your email for your gift of '+str(game.game)+ '<br>'+diagnostic)
    return HttpResponse('huh?')
def auto_get(request):
    if request.GET.get('code'):
        
        code = get_object_or_404(Code, uuid = request.GET.get('code'))
        previously_claimed = ""
        if code.uuid_claimed == True:
            previously_claimed = 'Warning! This code may have been used already!'
        code.uuid_claimed = True
        code.save()
        return HttpResponse(code.game.notes + '<br>Code: '+ code.code +'<br>'+ previously_claimed)
    else:
        return HttpResponse('huh?')

def auto_return(request):
    if request.method == 'POST':
        code = get_object_or_404(Code, uuid = request.POST.get('uuid'))
        if code.uuid_claimed:
            return HttpResponse('The only way you\'re reading this is if you did something kinda shady. Why are you trying to break things?')
 
        if 'return_code' in request.POST:
            code.uuid_reset()
            code.game.update_count()
            return HttpResponse('returned')
        elif 'keep_code' in request.POST:
            return HttpResponse('kept') 
        else:
            return redirect('/')
    if request.GET.get('code'):
        #fetch by uuid (cunningly named "code" in request because I am a bad)
        code = get_object_or_404(Code, uuid = request.GET.get('code'))
        if code.uuid_claimed:
            return HttpResponse('Cannot return! Code already claimed!')
        context = {
            'game': code.game.game,
            'uuid': request.GET.get('code'),
        }
        return render(request, 'dispenser/auto_return.html', context)
    else:
        return HttpResponse('huh?')
    return HttpResponse('auto return placeholder')

def raffle(request):

    return HttpResponse('public raffle placeholder')

def export(request, game_id):
    return HttpResponse('nope') 

##helper functions

def _process_code(assigned, code, used, codepocalypse):
    code = Code.objects.get(code = code)
    code.assigned = assigned
    code.codepocalypse = codepocalypse
    code.used = used
    code.save()

def get_notes(request, game_id):
    try:
        notes = GameCodeProfile.objects.get(id = game_id).notes
        return HttpResponse(notes)
    except:
        return HttpResponse(False)
