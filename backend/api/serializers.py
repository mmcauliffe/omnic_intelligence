from rest_framework import serializers
from . import models
from django.contrib.auth.models import User, Group
from django.db.models import Sum, F


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        depth = 2
        fields = ('id', 'first_name', 'last_name', 'username', 'is_superuser')


class HeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Hero
        fields = '__all__'


class HeroAbilitySerializer(serializers.ModelSerializer):
    damaging_abilities = serializers.SerializerMethodField()
    reviving_abilities = serializers.SerializerMethodField()
    denying_abilities = serializers.SerializerMethodField()
    deniable_abilities = serializers.SerializerMethodField()
    npcs = serializers.SerializerMethodField()

    class Meta:
        model = models.Hero
        fields = ('id', 'name', 'type', 'ability_denier',
                  'damaging_abilities', 'reviving_abilities', 'denying_abilities', 'deniable_abilities',
                  'npcs'
                  )

    def get_damaging_abilities(self, obj):
        return AbilityDisplaySerializer(obj.abilities.filter(type=models.Ability.DAMAGING_TYPE).all(), many=True).data

    def get_reviving_abilities(self, obj):
        return AbilityDisplaySerializer(obj.abilities.filter(type=models.Ability.REVIVING_TYPE).all(), many=True).data

    def get_denying_abilities(self, obj):
        return AbilityDisplaySerializer(obj.abilities.filter(type=models.Ability.DENYING_TYPE).all(), many=True).data

    def get_deniable_abilities(self, obj):
        return AbilityDisplaySerializer(obj.abilities.filter(deniable=True).all(), many=True).data

    def get_npcs(self, obj):
        return NPCHerolessSerializer(obj.npc_set.all(), many=True).data


class AbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ability
        fields = '__all__'


class AbilityDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ability
        fields = ('id', 'name', 'type', 'headshot_capable', 'ultimate', 'deniable')


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


class NPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NPC
        fields = '__all__'


class NPCHerolessSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NPC
        fields = ('id', 'name')


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
    match = MatchSerializer()
    map = MapSerializer()
    left_team = TeamParticipationSerializer()
    right_team = TeamParticipationSerializer()
    name = serializers.SerializerMethodField()

    class Meta:
        model = models.Game
        fields = ('id', 'name', 'game_number', 'match', 'left_team', 'right_team', 'map')

    def get_name(self, obj):
        teams = obj.match.teams.all()
        return 'Game {} of {} vs {} on {}'.format(obj.game_number, teams[0].name, teams[1].name, obj.map.name)


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
            'id', 'round_number', 'game', 'attacking_side', 'begin', 'end', 'stream_vod', 'annotation_status',
            'sequences')

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
            'id', 'round_number', 'game', 'attacking_side', 'begin', 'end', 'annotation_status',
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
    game = GameDisplaySerializer()
    stream_vod = StreamVodSerializer()
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
        return obj.get_heroes_used()

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
        return [x.get_hero_at_timepoint(obj.round, obj.time_point).name for x in obj.assisting_players.all()]


class KillFeedEventDisplaySerializer(serializers.ModelSerializer):
    killing_player = serializers.StringRelatedField()
    killed_player = serializers.StringRelatedField()
    ability = serializers.StringRelatedField()

    class Meta:
        model = models.KillFeedEvent
        fields = '__all__'


class KillFeedEventEditSerializer(serializers.ModelSerializer):
    #killing_player = PlayerSerializer()
    dying_player = PlayerSerializer()
    #dying_player = serializers.StringRelatedField()
    denied_ult = serializers.StringRelatedField()
    ability = AbilityDisplaySerializer()
    #possible_abilities = AbilitySerializer(many=True)
    #possible_assists = PlayerSerializer(many=True)
    #possible_killing_players = PlayerSerializer(many=True)
    #possible_dying_npcs = NPCSerializer(many=True)
    # assisting_players = PlayerSerializer(many=True)

    class Meta:
        model = models.KillFeedEvent
        fields = ('id', 'time_point', 'killing_player', 'dying_player', 'ability', 'headshot',
                  #'possible_abilities',
                  #'possible_assists',
                  'assisting_players', 'dying_npc', 'denied_ult',
                  #'possible_killing_players',
                  #'possible_dying_npcs'
                  )


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
