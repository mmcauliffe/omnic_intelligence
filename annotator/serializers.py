from rest_framework import serializers
from . import models


class HeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Hero
        fields = '__all__'


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Map
        fields = '__all__'


class AbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ability
        fields = '__all__'


class NPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NPC
        fields = '__all__'


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Player
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Team
        fields = '__all__'


class PlayerParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlayerParticipation
        fields = ('player', 'player_index')


class TeamParticipationSerializer(serializers.ModelSerializer):
    players = PlayerParticipationSerializer(source='playerparticipation_set', many=True)

    class Meta:
        model = models.TeamParticipation
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Event
        fields = '__all__'


class GameSerializer(serializers.ModelSerializer):
    left_team = TeamParticipationSerializer()
    right_team = TeamParticipationSerializer()
    vod_link = serializers.ReadOnlyField()

    class Meta:
        model = models.Game
        fields = ('id', 'game_number', 'match', 'left_team', 'right_team', 'map', 'vod', 'vod_link')

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


class MatchSerializer(serializers.ModelSerializer):
    # teams = serializers.StringRelatedField(many=True)

    class Meta:
        model = models.Match
        fields = '__all__'


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Round
        fields = ('id', 'round_number', 'game', 'attacking_side', 'begin', 'end', 'vod', 'vod_link')


class SwitchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Switch
        fields = '__all__'


class SwitchDisplaySerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    new_hero = HeroSerializer()

    class Meta:
        model = models.Switch
        fields = '__all__'


class DeathSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Death
        fields = '__all__'


class DeathDisplaySerializer(serializers.ModelSerializer):
    player = serializers.StringRelatedField()

    class Meta:
        model = models.Death
        fields = '__all__'


class PauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pause
        fields = '__all__'


class UnpauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Unpause
        fields = '__all__'


class ReplayStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReplayStart
        fields = '__all__'


class ReplayEndSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReplayEnd
        fields = '__all__'


class OvertimeStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OvertimeStart
        fields = '__all__'


class KillSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Kill
        fields = '__all__'


class KillDisplaySerializer(serializers.ModelSerializer):
    killing_player = serializers.StringRelatedField()
    killed_player = serializers.StringRelatedField()
    ability = serializers.StringRelatedField()

    class Meta:
        model = models.Kill
        fields = '__all__'


class ReviveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Revive
        fields = '__all__'


class ReviveDisplaySerializer(serializers.ModelSerializer):
    reviving_player = serializers.StringRelatedField()
    revived_player = serializers.StringRelatedField()
    ability = serializers.StringRelatedField()

    class Meta:
        model = models.Revive
        fields = '__all__'


class UltGainSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UltGain
        fields = '__all__'


class UltGainDisplaySerializer(serializers.ModelSerializer):
    player = PlayerSerializer()

    class Meta:
        model = models.UltGain
        fields = '__all__'


class UltUseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UltUse
        fields = '__all__'


class UltUseDisplaySerializer(serializers.ModelSerializer):
    player = PlayerSerializer()

    class Meta:
        model = models.UltUse
        fields = '__all__'


class PointGainSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PointGain
        fields = '__all__'


class PointFlipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PointFlip
        fields = '__all__'


class KillNPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.KillNPC
        fields = '__all__'


class KillNPCDisplaySerializer(serializers.ModelSerializer):
    killing_player = serializers.StringRelatedField()
    killed_npc = serializers.StringRelatedField()
    ability = serializers.StringRelatedField()

    class Meta:
        model = models.KillNPC
        fields = '__all__'


class NPCDeathSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NPCDeath
        fields = '__all__'


class NPCDeathDisplaySerializer(serializers.ModelSerializer):
    npc = serializers.StringRelatedField()

    class Meta:
        model = models.NPCDeath
        fields = '__all__'
