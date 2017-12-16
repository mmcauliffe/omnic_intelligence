from rest_framework import serializers
from .models import Event, Match, Player, Team, Map, Game, Round, TeamParticipation, PlayerParticipation, Pause, \
    Unpause, Switch, Kill, Revive, UltGain, UltUse, PointGain, PointFlip, Hero, Death, KillNPC, NPC, NPCDeath


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class MatchSerializer(serializers.ModelSerializer):
    teams = serializers.StringRelatedField(many=True)

    class Meta:
        model = Match
        fields = '__all__'


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = '__all__'


class SwitchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Switch
        fields = '__all__'


class DeathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Death
        fields = '__all__'


class PauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pause
        fields = '__all__'


class UnpauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unpause
        fields = '__all__'


class KillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kill
        fields = '__all__'


class ReviveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Revive
        fields = '__all__'


class UltGainSerializer(serializers.ModelSerializer):
    class Meta:
        model = UltGain
        fields = '__all__'


class UltUseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UltUse
        fields = '__all__'


class PointGainSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointGain
        fields = '__all__'


class PointFlipSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointFlip
        fields = '__all__'


class KillNPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KillNPC
        fields = '__all__'


class NPCDeathSerializer(serializers.ModelSerializer):
    class Meta:
        model = NPCDeath
        fields = '__all__'
