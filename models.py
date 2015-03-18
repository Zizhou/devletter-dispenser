from django.db import models
from django.db.models.signals import post_save
from django import forms

from submit.models import Game

import uuid, datetime
# Create your models here.

#somehow, I don't think this is how models should be used
class Settings(models.Model):
    global_url = models.CharField(max_length = 200, blank = True)
    donation_id = models.IntegerField(default = 0)

class GameCodeProfile(models.Model):
    game = models.ForeignKey(Game)
    count = models.IntegerField(default = 0)
    notes = models.TextField(blank = True)

    def __unicode__(self):
        return unicode(self.game) + " (" + unicode(self.count) + ")"
    
    def update_count(self):
        self.count = self.code_set.exclude(used = True).count() 
        self.save()

    def get_code(self):
        new_code = Code.objects.filter(game = self.id).exclude(used = True)
        if new_code.count() == 0:
            return False
        else:
            return new_code[0]
    def get_all_codes(self):
        all_code = Code.objects.filter(game = self.id)
        return all_code
         


class Code(models.Model):
    game = models.ForeignKey(GameCodeProfile)
    code = models.CharField(max_length = 200, unique = True)
    used = models.BooleanField(default = False, blank = True)
    codepocalypse = models.BooleanField(default = False, blank = True)
    #could also be FK, but I think that's overkill
    #can always just make a query for a batch
    assigned = models.CharField(max_length = 200, blank = True)

    uuid = models.CharField(max_length = 200, unique = True, blank = True, null = True)
    uuid_assigned = models.BooleanField(default = False, blank = True)
    uuid_claimed = models.BooleanField(default = False, blank = True)
    uuid_expired = models.DateTimeField(default = datetime.datetime(2038, 1,1,0,0,0, 0, None),blank = True)
    def __unicode__(self):
        return unicode(self.game.game) + self.code + unicode(self.assigned)
    #recipient should be email address, else Bad Things happen
    def uuid_assign(self, recipient):
        if self.uuid_claimed or self.uuid_assigned:
            return False
        self.used = True
        self.assigned = recipient
        self.uuid_assigned = True
        self.uuid_expired = datetime.datetime.utcnow() + datetime.timedelta(7)
        self.save()
        print 'resetting ' + str(self.game)
        return True

    def uuid_reset(self):
        if self.uuid_claimed:
            return False
        self.uuid_assigned = False
        self.assigned = ''
        self.used = False
        self.uuid_expired = datetime.datetime(2038, 1,1,0,0,0,0,None)
        create_uuid(self)
        self.save()
        return True

    class Meta:
        permissions = (
            ('can_access', 'Can access codes'),
        )
        #gah
        ordering = ['game__game__name']

class AutoRaffle(models.Model):
    contest_id = models.CharField(max_length = 200, unique = True, blank = True, null = True)
    

class RaffleMail(models.Model):
    mail = models.EmailField(max_length = 254, unique = False)
    
    class Meta:
        ordering = ['mail']

##Forms
#I should really just split these into seperate files
    
class CodeForm(forms.Form):
    gameselect = forms.ModelChoiceField(queryset = GameCodeProfile.objects.all().order_by('game__name'), label = 'Select a game to add codes to:')
    codeblock = forms.CharField(widget = forms.Textarea, label = 'Enter code(s):')
    #js will pull out current notes, if any
    notes = forms.CharField(required = False, widget = forms.Textarea,  label = 'Notes regarding codes:')#, attrs={'id':'code_notes',}
    #splits block of codes by newline
    def code_split(self):
        code_list = []
        for code in self.cleaned_data['codeblock'].splitlines():
            print code
            if code != '':
                code_list.append(code)
        return code_list

    #processes codeblock into individual codes
    def code_save(self):
        game = self.cleaned_data['gameselect']
        game.notes = self.cleaned_data['notes']
        game.save()
        invalid = []
        for code in self.code_split():
            try:
                c = Code(game = game, code = code)
                c.save()
            except:
                invalid.append(code)
                continue
        return invalid

class GameSelectForm(forms.Form):
    gameselect = forms.ModelChoiceField(queryset = GameCodeProfile.objects.exclude(count = 0).order_by('game__name'), label = 'Select a game to get codes from:')

class GetCodeForm(forms.Form):
    code = forms.CharField(max_length = 200, label = 'Code:', widget = forms.TextInput(attrs={'readonly':'readonly'}))
    assigned = forms.CharField(max_length = 500, label = 'This code is going to:')

#    used = forms.BooleanField(label = 'Check box to confirm assignment:')
    used = forms.BooleanField(required = False, widget = forms.HiddenInput())
    codepocalypse = forms.BooleanField(required = False, widget = forms.HiddenInput())

class GetWinnerForm(forms.Form):
    winner = forms.CharField(max_length = 500, label = 'Search for code recepient:')

    def get_winner(self):
        person = self.cleaned_data['winner']
        #"filter" is totally not going to cause problems in the future. nope.
        entry = Code.objects.filter(assigned__iexact = person)
        return entry

class EnterRaffle(forms.Form):
    mail = forms.EmailField(label = 'Shady E-Mail Form For Fantabulous Prizes:')
    
class StartRaffle(forms.Form):
    mail = 0    
##magic signals

#create code profiles when a new game is created
def game_create(sender, instance, created, **kwargs):
    if created == True:
        g = GameCodeProfile(game = instance)
        g.save()

post_save.connect(game_create, sender = Game)

#auto increment count on creation of code instance
def count_increment(sender, instance, created, **kwargs):
    if created == True:
        gcp = instance.game
        gcp.count += 1
        gcp.save()

post_save.connect(count_increment, sender = Code)

#creates new uuid for each new code
def code_uuid(sender, instance, created, **kwargs):
    if created == True:
        create_uuid(instance)

post_save.connect(code_uuid, sender = Code)

#creates uuids(hopefully unique? ehhhhhh...)
def create_uuid(code):
    code.uuid = uuid.uuid4()#random uuid however the python lib does that
    code.save() 
