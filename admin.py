from django.contrib import admin

from dispenser.models import GameCodeProfile, Code

# Register your models here.

class GameCodeProfileAdmin(admin.ModelAdmin):
    fields = ['game', 'count', 'notes']

class CodeAdmin(admin.ModelAdmin):
   fields = ['game', 'code', 'used', 'assigned', 'codepocalypse']

admin.site.register(GameCodeProfile, GameCodeProfileAdmin)
admin.site.register(Code, CodeAdmin)
