from django.contrib import admin
# Register your models here.
from .models import Map, Hero, Ability, NPC, Team, Player, Event, Match, Round, StreamChannel, StreamVod, TeamParticipation, Affiliation, Game


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

class AffiliationInline(admin.TabularInline):
    model = Affiliation

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = (AffiliationInline,)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'wl_id')
    readonly_fields = ('id',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(StreamChannel)
class StreamChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'site')

    def get_site_name(self, obj):
        return obj.get_site_name()


@admin.register(StreamVod)
class StreamVodAdmin(admin.ModelAdmin):
    list_display = ('id', 'channel', 'title', 'broadcast_date')

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'match', 'game_number')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'wl_id','get_event_name', 'get_event_spectator_mode', 'get_team_description')

    def get_event_name(self, obj):
        return obj.event.name
    get_event_name.admin_order_field  = 'event__name'  #Allows column order sorting
    get_event_name.short_description = 'Event name'  #Renames column head

    def get_event_spectator_mode(self, obj):
        return obj.event.get_spectator_mode_display()
    get_event_spectator_mode.admin_order_field  = 'event__spectator_mode'  #Allows column order sorting
    get_event_spectator_mode.short_description = 'Event spectator'  #Renames column head

    def get_team_description(self, obj):
        return obj.team_description
    get_team_description.admin_order_field  = 'teams'  #Allows column order sorting
    get_team_description.short_description = 'Team description'  #Renames column head


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('id', 'round_number', 'get_game_number', 'get_match_wl_id', 'get_event_name', 'annotation_status')

    def get_game_number(self, obj):
        return obj.game.game_number
    get_game_number.admin_order_field  = 'game__game_number'  #Allows column order sorting
    get_game_number.short_description = 'Game number'  #Renames column head

    def get_match_wl_id(self, obj):
        return obj.game.match.wl_id
    get_match_wl_id.admin_order_field  = 'game__match__wl_id'  #Allows column order sorting
    get_match_wl_id.short_description = 'Match WL'  #Renames column head

    def get_event_name(self, obj):
        return obj.game.match.event.name
    get_event_name.admin_order_field  = 'game__match__event__name'  #Allows column order sorting
    get_event_name.short_description = 'Event'  #Renames column head
