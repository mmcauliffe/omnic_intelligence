from rest_framework import serializers
from . import models
from django.contrib.auth.models import User, Group
from django.db.models import Sum, F
from django.conf import settings
import re


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        depth = 2
        fields = ('id', 'first_name', 'last_name', 'username', 'is_superuser')


class HeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Hero
        fields = '__all__'


class AbilityDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ability
        fields = ('id', 'name', 'type', 'headshot_capable', 'ultimate', 'deniable')


class NPCHerolessSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NPC
        fields = ('id', 'name')


class HeroAbilitySerializer(serializers.ModelSerializer):
    abilities = AbilityDisplaySerializer(many=True)
    npc_set = NPCHerolessSerializer(many=True)

    class Meta:
        model = models.Hero
        fields = ('id', 'name', 'type', 'ability_denier',
                  'abilities',
                  'npc_set'
                  )


class AbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ability
        fields = '__all__'

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Status
        fields = '__all__'


class HeroSummarySerializer(serializers.ModelSerializer):
    abilities = serializers.SerializerMethodField()
    play_time = serializers.SerializerMethodField()

    class Meta:
        model = models.Hero
        fields = ('id', 'name', 'abilities', 'play_time')

    def get_abilities(self, obj):
        return AbilitySerializer(obj.abilities.all(), many=True).data

    def get_play_time(self, obj):
        return obj.switch_set.aggregate(total=Sum(F('end_time_point') - F('time_point')))['total']


class MapSerializer(serializers.ModelSerializer):
    mode = serializers.SerializerMethodField()

    class Meta:
        model = models.Map
        fields = '__all__'

    def get_mode(self, obj):
        return obj.get_mode_display()


class SubmapSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Submap
        fields = '__all__'


class NPCSerializer(serializers.ModelSerializer):
    spawning_hero = HeroSerializer()
    class Meta:
        model = models.NPC
        fields = '__all__'


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Player
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True)

    class Meta:
        model = models.Team
        fields = '__all__'


class PlayerParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlayerParticipation
        fields = ('player', 'player_index')


class TeamParticipationSerializer(serializers.ModelSerializer):
    players = PlayerParticipationSerializer(source='playerparticipation_set', many=True)
    color = serializers.SerializerMethodField()

    class Meta:
        model = models.TeamParticipation
        fields = '__all__'

    def get_color(self, obj):
        return obj.get_color_display()


class TeamParticipationEditSerializer(serializers.ModelSerializer):
    players = PlayerParticipationSerializer(source='playerparticipation_set', many=True)

    class Meta:
        model = models.TeamParticipation
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(many=True)

    class Meta:
        model = models.Event
        fields = '__all__'


class EventDisplaySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Event
        fields = ('id', 'name', 'spectator_mode', 'film_format')


class MatchSerializer(serializers.ModelSerializer):
    event = EventSerializer()
    teams = serializers.StringRelatedField(many=True)
    name = serializers.SerializerMethodField()

    start_time = serializers.DecimalField(10, 1)

    class Meta:
        model = models.Match
        fields = ('id', 'event', 'teams', 'start_time', 'name')

    def get_name(self, obj):
        teams = obj.teams.all()
        return '{} vs {}'.format(teams[0].name, teams[1].name)


class MatchDisplaySerializer(serializers.ModelSerializer):
    event = EventDisplaySerializer()
    teams = serializers.StringRelatedField(many=True)
    name = serializers.SerializerMethodField()

    start_time = serializers.DecimalField(10, 1)

    class Meta:
        model = models.Match
        fields = ('id', 'event', 'teams', 'start_time', 'name')

    def get_name(self, obj):
        teams = obj.teams.all()
        return '{} vs {}'.format(teams[0].name, teams[1].name)


class MatchEditSerializer(serializers.ModelSerializer):
    event = EventSerializer()
    name = serializers.SerializerMethodField()
    teams = serializers.SerializerMethodField()

    start_time = serializers.DecimalField(10, 1)

    class Meta:
        model = models.Match
        fields = ('id', 'event', 'teams', 'start_time', 'name')

    def get_name(self, obj):
        teams = obj.teams.all()
        return '{} vs {}'.format(teams[0].name, teams[1].name)

    def get_teams(self, obj):
        teams = obj.teams.all()
        return {i:x.id for i,x in enumerate(teams)}


class GameDisplaySerializer(serializers.ModelSerializer):
    match = MatchDisplaySerializer()
    map = MapSerializer()
    left_team = TeamParticipationSerializer()
    right_team = TeamParticipationSerializer()
    left_team_color_hex = serializers.SerializerMethodField()
    right_team_color_hex = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.Game
        fields = ('id', 'name', 'game_number', 'match', 'left_team', 'right_team',
                  'left_team_color_hex', 'right_team_color_hex', 'map')

    def get_name(self, obj):
        teams = obj.match.teams.all()
        return 'Game {} of {} vs {} on {}'.format(obj.game_number, teams[0].name, teams[1].name, obj.map.name)

    def get_left_team_color_hex(self, obj):
        return obj.left_team.get_color_hex(obj.match.event.spectator_mode)

    def get_right_team_color_hex(self, obj):
        return obj.right_team.get_color_hex(obj.match.event.spectator_mode)


class GameEditSerializer(serializers.ModelSerializer):
    left_team = TeamParticipationEditSerializer()
    right_team = TeamParticipationEditSerializer()
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.Game
        fields = ('id', 'name', 'game_number', 'match', 'left_team', 'right_team', 'map')

    def get_name(self, obj):
        teams = obj.match.teams.all()
        return 'Game {} of {} vs {} on {}'.format(obj.game_number, teams[0].name, teams[1].name, obj.map.name)


class GameSerializer(serializers.ModelSerializer):
    left_team = TeamParticipationSerializer()
    right_team = TeamParticipationSerializer()
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.Game
        fields = ('id', 'name', 'game_number', 'match', 'left_team', 'right_team', 'map')

    def get_name(self, obj):
        teams = obj.match.teams.all()
        return 'Game {} of {} vs {} on {}'.format(obj.game_number, teams[0].name, teams[1].name, obj.map.name)

    def create(self, validated_data):
        left_team_data = validated_data.pop('left_team')
        try:
            left_player_data = left_team_data.pop('playerparticipation_set')
        except KeyError:
            left_player_data = []
        left_team_participation = models.TeamParticipation.objects.create(**left_team_data)
        for player in left_player_data:
            models.PlayerParticipation.objects.create(team_participation=left_team_participation, **player)

        right_team_data = validated_data.pop('right_team')
        try:
            right_player_data = right_team_data.pop('playerparticipation_set')
        except KeyError:
            right_player_data = []
        right_team_participation = models.TeamParticipation.objects.create(**right_team_data)
        for player in right_player_data:
            models.PlayerParticipation.objects.create(team_participation=right_team_participation, **player)
        game = models.Game.objects.create(left_team=left_team_participation, right_team=right_team_participation,
                                          **validated_data)
        return game

    def update(self, instance, validated_data):
        print(validated_data)
        left_team_data = validated_data.pop('left_team')
        try:
            left_player_data = left_team_data.pop('playerparticipation_set')
        except KeyError:
            left_player_data = []
        right_team_data = validated_data.pop('right_team')
        try:
            right_player_data = right_team_data.pop('playerparticipation_set')
        except KeyError:
            right_player_data = []

        for item in validated_data:
            if models.Game._meta.get_field(item):
                setattr(instance, item, validated_data[item])
        for item in left_team_data:
            if models.TeamParticipation._meta.get_field(item):
                setattr(instance.left_team, item, left_team_data[item])
        for item in right_team_data:
            if models.TeamParticipation._meta.get_field(item):
                setattr(instance.right_team, item, right_team_data[item])
        models.PlayerParticipation.objects.filter(team_participation=instance.left_team).delete()
        models.PlayerParticipation.objects.filter(team_participation=instance.right_team).delete()
        for player in left_player_data:
            models.PlayerParticipation.objects.create(team_participation=instance.left_team, **player)
        for player in right_player_data:
            models.PlayerParticipation.objects.create(team_participation=instance.right_team, **player)

        instance.save()
        instance.left_team.save()
        instance.right_team.save()
        return instance


class StreamChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StreamChannel
        fields = '__all__'


class RoundSerializer(serializers.ModelSerializer):
    # game = GameSerializer()
    class Meta:
        model = models.Round
        fields = (
            'id', 'round_number', 'game', 'attacking_side', 'submap',
            'begin', 'end', 'stream_vod', 'annotation_status',
            'sequences')

class RoundAnalysisSerializer(serializers.ModelSerializer):
    film_format = serializers.SerializerMethodField()
    spectator_mode = serializers.SerializerMethodField()
    map = serializers.SerializerMethodField()

    class Meta:
        model = models.Round
        fields = ('id', 'map', 'duration', 'film_format', 'spectator_mode')

    def get_film_format(self, obj):
        if obj.stream_vod is None:
            return ''
        return obj.stream_vod.get_film_format_display()

    def get_spectator_mode(self, obj):
        return obj.game.match.event.get_spectator_mode_display()

    def get_map(self, obj):
        return obj.game.map.name

class StreamVodSerializer(serializers.ModelSerializer):
    rounds = RoundSerializer(many=True)
    games = GameEditSerializer(many=True)
    matches = MatchSerializer(many=True)
    class Meta:
        model = models.StreamVod
        fields = ('id', 'title', 'url', 'broadcast_date', 'vod_link', 'film_format', 'sequences',
                  'channel', 'status', 'type', 'rounds', 'games', 'matches')


class VodDisplaySerializer(serializers.ModelSerializer):
    channel = StreamChannelSerializer()

    class Meta:
        model = models.StreamVod
        fields = ('id', 'title', 'url', 'broadcast_date', 'vod_link', 'film_format',
                  'sequences', 'channel', 'status', 'type')


class AnnotateVodSerializer(serializers.ModelSerializer):
    channel = StreamChannelSerializer()
    teams = serializers.SerializerMethodField()

    class Meta:
        model = models.StreamVod
        fields = ('id', 'title', 'url', 'broadcast_date', 'vod_link', 'film_format',
                  'sequences', 'channel', 'status', 'type', 'teams')

    def get_teams(self, obj):
        owl_mapping = {'DAL': 'Dallas Fuel',
                       'PHI': 'Philadelphia Fusion', 'SEO': 'Seoul Dynasty',
                       'LDN': 'London Spitfire', 'SFS': 'San Francisco Shock', 'HOU': 'Houston Outlaws',
                       'BOS': 'Boston Uprising', 'VAL': 'Los Angeles Valiant', 'GLA': 'Los Angeles Gladiators',
                       'FLA': 'Florida Mayhem', 'SHD': 'Shanghai Dragons', 'NYE': 'New York Excelsior',
                       'PAR': 'Paris Eternal', 'TOR': 'Toronto Defiant', 'WAS': 'Washington Justice',
                       'VAN': 'Vancouver Titans', 'CDH': 'Chengdu Hunters', 'HZS': 'Hangzhou Spark',
                       'ATL': 'Atlanta Reign', 'GZC': 'Guangzhou Charge',
                       'CHE': 'Chengdu Hunters', 'GUA': 'Guangzhou Charge', 'HAN': 'Hangzhou Spark'}
        patterns = []
        if obj.channel.name.lower() in ['overwatchcontenders', 'overwatchcontendersbr']:
            patterns.append(r'''(?P<team_one>[-\w ']+) (vs|V) (?P<team_two>[-\w ']+) \| (?P<desc>[\w ]+) Game (?P<game_num>\d) \| ((?P<sub>[\w :]+) \| )?(?P<main>[\w ]+)''')
        elif obj.channel.name.lower() == 'overwatch contenders':
            patterns.append(r'''(?P<team_one>[-\w .']+) (vs|V) (?P<team_two>[-\w .']+) (\(Part)?.*''')
        elif obj.channel.name.lower() == 'overwatchleague':
            patterns.append(r'Game [#]?(\d+) (?P<team_one>\w+) @ (?P<team_two>\w+) \| ([\w ]+)')
        elif obj.channel.name.lower() == 'owlettournament':
            patterns.append(r'''.* - (?P<team_one>[-\w ']+) (vs[.]?|V) (?P<team_two>[-\w ']+)''')
        elif obj.channel.name.lower() =='owlet tournament':
            patterns.append(r'''.*: (?P<team_one>[-\w ']+) (vs[.]?|V) (?P<team_two>[-\w ']+)''')
        elif obj.channel.name.lower() == 'rivalcade':
            patterns.append(r'''.*, (?P<team_one>[-\w '?]+) (vs[.]?|VS) (?P<team_two>[-\w '?]+)''')
        patterns.append(r'''(.*[-,:] )?(?P<team_one>[\w '?]+) (vs[.]?|VS) (?P<team_two>[\w '?]+)( [-].*)?''')
        for pattern in patterns:
            m = re.match(pattern, obj.title)
            team_one_data = None
            team_two_data = None
            if m is not None:
                team_one = m.group('team_one').strip()
                if team_one in owl_mapping:
                    team_one = owl_mapping[team_one]
                team_two = m.group('team_two').strip()
                if team_two in owl_mapping:
                    team_two = owl_mapping[team_two]
                team_one = team_one.lower()
                team_two = team_two.lower()
                try:
                    team_one = models.Team.objects.get(name__iexact=team_one)
                    team_one_data = TeamSerializer(team_one).data
                except models.Team.DoesNotExist:
                    print("Could not find '{}'".format(team_one))
                try:
                    team_two = models.Team.objects.get(name__iexact=team_two)
                    team_two_data = TeamSerializer(team_two).data
                except models.Team.DoesNotExist:
                    print("Could not find '{}'".format(team_two))
                break
        return team_one_data, team_two_data


class EventVodDisplaySerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    film_format = serializers.SerializerMethodField()

    class Meta:
        model = models.StreamVod
        fields = ('id', 'title', 'url', 'broadcast_date', 'vod_link', 'film_format',
                  'channel', 'status', 'type')

    def get_type(self, obj):
        return obj.get_type_display()

    def get_status(self, obj):
        return obj.get_status_display()

    def get_film_format(self, obj):
        return obj.get_film_format_display()


class VodAnnotateSerializer(serializers.ModelSerializer):
    rounds = serializers.SerializerMethodField()

    class Meta:
        model = models.StreamVod
        fields = ('id', 'title', 'url', 'broadcast_date', 'vod_link', 'film_format',
                  'sequences', 'channel', 'status', 'type', 'rounds')

    def get_rounds(self, obj):
        unnanotated_rounds = obj.round_set.filter(annotation_status='N')
        return RoundDisplaySerializer(unnanotated_rounds, many=True).data


class VodStatusSerializer(serializers.ModelSerializer):
    channel = StreamChannelSerializer()

    class Meta:
        model = models.StreamVod
        fields = ('id', 'title', 'url', 'broadcast_date', 'vod_link', 'film_format', 'channel')


class RoundDisplaySerializer(serializers.ModelSerializer):
    game = GameDisplaySerializer()
    spectator_mode = serializers.SerializerMethodField()
    stream_vod = VodDisplaySerializer()

    class Meta:
        model = models.Round
        fields = (
            'id', 'round_number', 'game', 'attacking_side', 'submap',
            'begin', 'end', 'annotation_status',
            'spectator_mode',
            'sequences', 'stream_vod')

    def get_spectator_mode(self, obj):
        return obj.game.match.event.get_spectator_mode_display()


class RoundEditSerializer(serializers.ModelSerializer):
    #game = GameDisplaySerializer()
    stream_vod = StreamVodSerializer()

    class Meta:
        model = models.Round
        fields = (
            'id', 'round_number', 'game', 'attacking_side', 'begin', 'end', 'stream_vod', 'annotation_status',
            'sequences')


class VodEditSerializer(serializers.ModelSerializer):
    rounds = serializers.SerializerMethodField()

    class Meta:
        model = models.StreamVod
        fields = ('id', 'title', 'url', 'broadcast_date', 'vod_link', 'film_format', 'sequences', 'channel', 'rounds')

    def get_rounds(self, obj):
        return RoundSerializer(obj.round_set.all(), many=True).data


class RoundStatusSerializer(serializers.ModelSerializer):
    stream_vod = EventVodDisplaySerializer()
    annotation_status = serializers.SerializerMethodField()
    attacking_side = serializers.SerializerMethodField()
    heroes_used = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = models.Round
        fields = ('id',
                  'round_number', 'game', 'attacking_side', 'begin', 'end', 'stream_vod', 'heroes_used',
                  'annotation_status', 'duration')

    def get_heroes_used(self, obj):
        d = obj.get_hero_play_time()
        return [{'name': x[0], 'play_time':x[1]} for x in sorted(d.items(), key=lambda x: -x[1])]

    def get_annotation_status(self, obj):
        return obj.get_annotation_status_display()

    def get_attacking_side(self, obj):
        return obj.get_attacking_side_display()

    def get_duration(self, obj):
        return obj.end - obj.begin


class HeroPickSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HeroPick
        fields = '__all__'


class HeroPickDisplaySerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    new_hero = HeroSerializer()

    class Meta:
        model = models.HeroPick
        fields = '__all__'


class PauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pause
        fields = '__all__'


class ReplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Replay
        fields = '__all__'


class OvertimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Overtime
        fields = '__all__'


class SmallerWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SmallerWindow
        fields = '__all__'


class ZoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Zoom
        fields = '__all__'


class KillFeedEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.KillFeedEvent
        fields = ('id', 'time_point', 'killing_player','ability', 'dying_player', )


class KillFeedSerializer(serializers.ModelSerializer):
    dying_entity = serializers.SerializerMethodField()
    dying_color = serializers.SerializerMethodField()
    killing_color = serializers.SerializerMethodField()
    killing_hero = serializers.SerializerMethodField()
    ability = serializers.StringRelatedField()
    assists = serializers.SerializerMethodField()

    class Meta:
        model = models.KillFeedEvent
        fields = (
            'time_point', 'killing_hero', 'killing_color', 'assists', 'ability', 'headshot', 'dying_entity',
            'dying_color')

    def get_dying_entity(self, obj):
        return obj.killed_player.get_hero_at_timepoint(obj.round, obj.time_point).name

    def get_dying_color(self, obj):
        if obj.killed_player in obj.round.game.left_team.players.all():
            return obj.round.game.left_team.get_color_display()
        else:
            return obj.round.game.right_team.get_color_display()

    def get_killing_hero(self, obj):
        return obj.killing_player.get_hero_at_timepoint(obj.round, obj.time_point).name

    def get_killing_color(self, obj):
        if obj.killing_player in obj.round.game.left_team.players.all():
            return obj.round.game.left_team.get_color_display()
        else:
            return obj.round.game.right_team.get_color_display()

    def get_assists(self, obj):
        return [x.player.get_hero_at_timepoint(obj.round, obj.time_point).name
                for x in models.Assist.objects.filter(kill=obj).all()]


class KillFeedEventDisplaySerializer(serializers.ModelSerializer):
    killing_player = serializers.StringRelatedField()
    killed_player = serializers.StringRelatedField()
    ability = serializers.StringRelatedField()

    class Meta:
        model = models.KillFeedEvent
        fields = '__all__'


class KillFeedEventEditSerializer(serializers.ModelSerializer):
    dying_player = PlayerSerializer()
    denied_ult = serializers.StringRelatedField()
    ability = AbilityDisplaySerializer()
    assists = serializers.SerializerMethodField()

    class Meta:
        model = models.KillFeedEvent
        fields = ('id', 'time_point', 'killing_player', 'dying_player', 'ability', 'headshot',
                  'assists', 'dying_npc', 'denied_ult',
                  )

    def get_assists(self, obj):
        return [x.player_id for x in models.Assist.objects.filter(kill=obj).all()]


class StatusEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StatusEffect
        fields = '__all__'


class StatusEffectDisplaySerializer(serializers.ModelSerializer):
    status = serializers.StringRelatedField()
    player = serializers.StringRelatedField()

    class Meta:
        model = models.StatusEffect
        fields = ('id', 'start_time', 'end_time', 'round', 'status', 'player')


class StatusEffectEditSerializer(serializers.ModelSerializer):
    status = StatusSerializer()
    player = PlayerSerializer()

    class Meta:
        model = models.StatusEffect
        fields = ('id', 'start_time', 'end_time', 'round', 'status', 'player')

class UltimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ultimate
        fields = '__all__'


class UltimateDisplaySerializer(serializers.ModelSerializer):
    player = PlayerSerializer()

    class Meta:
        model = models.Ultimate
        fields = '__all__'



class PointGainSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PointGain
        fields = '__all__'


class PointFlipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PointFlip
        fields = '__all__'


# AUTH

class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        depth = 1


class UserWithFullGroupsSerializer(serializers.ModelSerializer):
    groups = UserGroupSerializer(many=True)

    class Meta:
        model = User
        depth = 2
        fields = ('id', 'first_name', 'last_name', 'username', 'groups', 'password', 'user_permissions', 'is_superuser',
                  'is_staff', 'is_active')


class UnauthorizedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        depth = 2
        fields = ('id', 'first_name', 'last_name', 'username', 'is_superuser')
