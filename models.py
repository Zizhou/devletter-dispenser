from django.db import models
from django.db.models.signals import post_save
from django import forms

from submit.models import Game
# Create your models here.

class GameCodeProfile(models.Model):
    game = models.ForeignKey(Game)
    count = models.IntegerField(default = 0)
    notes = models.TextField(blank = True)

    def __unicode__(self):
        return unicode(self.game) + " (" + unicode(self.count) + ")"

class Code(models.Model):
    game = models.ForeignKey(GameCodeProfile)
    code = models.CharField(max_length = 200, unique = True)
    used = models.BooleanField(default = False)
    #could also be FK, but I think that's overkill
    #can always just make a query for a batch
    assigned = models.CharField(max_length = 200, blank = True)

    def __unicode__(self):
        return unicode(self.game.game) + self.code

    class Meta:
        permissions = (
            ('can_access', 'Can access codes'),
        )

class CodeForm(forms.Form):
    gameselect = forms.ModelChoiceField(queryset = GameCodeProfile.objects.all().order_by('game__name'), label = 'Select a game to add codes to:')
    codeblock = forms.CharField(widget = forms.Textarea, label = 'Enter code(s):')
    #js will pull out current notes, if any
    notes = forms.CharField(widget = forms.Textarea,  label = 'Notes regarding codes:')#, attrs={'id':'code_notes',}
    def code_split(textblock):
        codes = []
        for code in textblock.splitlines():
            codes.append(code)
        return codes

#magic signals

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
