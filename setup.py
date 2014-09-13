from submit.models import Game
from dispenser.models import GameCodeProfile

if GameCodeProfile.objects.all().count() == 0:
    for g in Game.objects.all():
        gcp = GameCodeProfile(game = g)
        gcp.save()
        print "done!"
else:
    print "GameCodeProfiles already exist, aborting"
