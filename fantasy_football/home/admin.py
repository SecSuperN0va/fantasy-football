from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass

@admin.register(Selection)
class SelectionAdmin(admin.ModelAdmin):
    pass

class SelectionInline(admin.TabularInline):
    model=Selection

@admin.register(FFLeague)
class FFLeagueAdmin(admin.ModelAdmin):
    filter_horizontal = ('players',)
    inlines = [
        SelectionInline
    ]

@admin.register(SportsLeague)
class SportsLeagueAdmin(admin.ModelAdmin):
    pass

@admin.register(TeamStanding)
class TeamStandingAdmin(admin.ModelAdmin):
    pass

class TeamStandingInline(admin.TabularInline):
    model=TeamStanding

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = [
        TeamStandingInline,
    ]
