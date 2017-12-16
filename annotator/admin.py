from django.contrib import admin
# Register your models here.
from .models import Map, Hero, Ability, NPC, Team, Player, Event, Match, Round


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ('name', 'mode')


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = ('name', 'hero_type')


@admin.register(Ability)
class AbilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'hero', 'damaging_ability', 'headshot_capable', 'revive_ability', 'ultimate_ability')


@admin.register(NPC)
class NPCAdmin(admin.ModelAdmin):
    pass


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    readonly_fields = ('id',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('wl_id',)


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    pass
