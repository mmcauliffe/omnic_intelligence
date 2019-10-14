from django.contrib import admin
# Register your models here.
from .models import Map, Hero, Ability, NPC, Team, Player, Event, Match, Round, StreamChannel, StreamVod, \
    TeamParticipation, Affiliation, Game, Status, StatusEffect, Patch


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    list_display = ('name', 'mode')


class AbilityInline(admin.TabularInline):
    model = Hero.abilities.through
    verbose_name = "Ability"
    verbose_name_plural = "Abilities"


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    inlines = [AbilityInline]


@admin.register(Ability)
class AbilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'headshot_capable',
                    'ultimate', 'deniable')


@admin.register(NPC)
class NPCAdmin(admin.ModelAdmin):
    pass


@admin.register(StatusEffect)
class StatusEffectAdmin(admin.ModelAdmin):
    list_display = ('id', 'round', 'get_status_name', 'start_time', 'end_time', 'player')

    def get_status_name(self, obj):
        return obj.status.name

    get_status_name.admin_order_field = 'status__name'  # Allows column order sorting
    get_status_name.short_description = 'Status name'  # Renames column head


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'independent')


class AffiliationInline(admin.TabularInline):
    model = Affiliation


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = (AffiliationInline,)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    readonly_fields = ('id',)


class TeamInline(admin.TabularInline):
    model = Event.teams.through
    verbose_name = "Team"
    verbose_name_plural = "Teams"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'spectator_mode', 'start_date', 'end_date')
    inlines = [TeamInline]


@admin.register(StreamChannel)
class StreamChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'site')

    def get_site_name(self, obj):
        return obj.get_site_name()


@admin.register(StreamVod)
class StreamVodAdmin(admin.ModelAdmin):
    list_display = ('id', 'channel', 'title', 'broadcast_date', 'film_format', 'status', 'type', 'last_modified')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'match', 'game_number')

@admin.register(Patch)
class PatchAdmin(admin.ModelAdmin):
    list_display = ('version_number', 'live_date', 'end_date')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_event_name', 'get_event_spectator_mode', 'get_team_description', 'date')

    def get_event_name(self, obj):
        return obj.event.name

    get_event_name.admin_order_field = 'event__name'  # Allows column order sorting
    get_event_name.short_description = 'Event name'  # Renames column head

    def get_event_spectator_mode(self, obj):
        return obj.event.get_spectator_mode_display()

    get_event_spectator_mode.admin_order_field = 'event__spectator_mode'  # Allows column order sorting
    get_event_spectator_mode.short_description = 'Event spectator'  # Renames column head

    def get_team_description(self, obj):
        return obj.team_description

    get_team_description.admin_order_field = 'teams'  # Allows column order sorting
    get_team_description.short_description = 'Team description'  # Renames column head


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('id', 'round_number', 'get_game_number', 'get_event_name', 'annotation_status')

    def get_game_number(self, obj):
        return obj.game.game_number

    get_game_number.admin_order_field = 'game__game_number'  # Allows column order sorting
    get_game_number.short_description = 'Game number'  # Renames column head

    def get_event_name(self, obj):
        return obj.game.match.event.name

    get_event_name.admin_order_field = 'game__match__event__name'  # Allows column order sorting
    get_event_name.short_description = 'Event'  # Renames column head
