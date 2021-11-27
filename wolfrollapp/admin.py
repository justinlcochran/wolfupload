from django.contrib import admin
from .models import Player, Role, GameParameters

# Register your models here.
admin.site.register(Player)
admin.site.register(Role)
admin.site.register(GameParameters)