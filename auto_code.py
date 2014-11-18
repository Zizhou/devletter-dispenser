from dispenser.models import Code, GameCodeProfile

GLOBAL_URL = 'http://devletter.net/dispenser/auto/'

class AutoCode():
    def __init__(self):
        #this should be tweaked
        self.code = Code()
        self.url_get = GLOBAL_URL + 'get?code='
        self.url_return = GLOBAL_URL + 'return?code='
        self.game = ''
    def __unicode__(self):
        return self.code

    def code_rand(self, assigned):
        game_profile = GameCodeProfile.objects.exclude(count = 0).order_by('?')[0]
        self.game = game_profile.game
        self.code = game_profile.get_code()
        self.code.uuid_assign(assigned)
        game_profile.update_count()
        return self.code

    def code_select(self, assigned, game_id):
        game_profile = GameCodeProfile.objects.get(id = game_id)
        self.game = game_profile.game
        if game_profile.count == 0:
            return False
        self.code = game_profile.get_code()
        self.code.uuid_assign(assigned)
        game_profile.update_count()
        return self.code

    def get_url_get(self):
        url_get = self.url_get + self.code.uuid
        return url_get

    def get_url_return(self):
        url_return = self.url_return + self.code.uuid
        return url_return
