from django.contrib import admin
from .models import Player, Role, GameParameters, SavedGame

# Register your models here.
admin.site.register(Player)
admin.site.register(Role)
admin.site.register(GameParameters)
admin.site.register(SavedGame)