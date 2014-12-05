from django.contrib import admin

from dispenser.models import GameCodeProfile, Code, Settings

# Register your models here.
class SettingsAdmin(admin.ModelAdmin):
    fields = ['global_url', 'donation_id']

class GameCodeProfileAdmin(admin.ModelAdmin):
    fields = ['game', 'count', 'notes']

class CodeAdmin(admin.ModelAdmin):
    fields = ['game', 'code', 'used', 'assigned', 'codepocalypse', 'uuid', 'uuid_assigned', 'uuid_claimed', 'uuid_expired']
    list_filter = ('uuid_assigned',)

admin.site.register(GameCodeProfile, GameCodeProfileAdmin)
admin.site.register(Code, CodeAdmin)
admin.site.register(Settings, SettingsAdmin)
