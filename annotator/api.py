from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from .serializers import MatchSerializer, RoundSerializer, SwitchSerializer, EventSerializer, GameSerializer, \
    DeathSerializer, UnpauseSerializer, UltUseSerializer, UltGainSerializer, ReviveSerializer, PointGainSerializer, \
    PointFlipSerializer, PauseSerializer, NPCDeathSerializer, KillSerializer, KillNPCSerializer
from .models import Event, Match, Player, Team, Map, Game, Round, TeamParticipation, PlayerParticipation, Pause, \
    Unpause, Switch, Kill, Revive, UltGain, UltUse, PointGain, PointFlip, Hero, Death, KillNPC, NPC, NPCDeath


class EventViewSet(viewsets.ModelViewSet):
    model = Event
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @detail_route(methods=['get'])
    def matches(self, request, pk=None):
        event = self.get_object()
        matches = event.match_set.prefetch_related('teams').all()
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)


class MatchViewSet(viewsets.ModelViewSet):
    model = Match
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

    @detail_route(methods=['get'])
    def games(self, request, pk=None):
        match = self.get_object()
        games = match.game_set.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)


class GameViewSet(viewsets.ModelViewSet):
    model = Game
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    @detail_route(methods=['get'])
    def rounds(self, request, pk=None):
        game = self.get_object()
        rounds = game.round_set.all()
        serializer = RoundSerializer(rounds, many=True)
        return Response(serializer.data)


class RoundViewSet(viewsets.ModelViewSet):
    model = Round
    queryset = Round.objects.all()
    serializer_class = RoundSerializer

    @detail_route(methods=['get'])
    def switches(self, request, pk=None):
        round = self.get_object()
        switches = round.switch_set.all()
        serializer = SwitchSerializer(switches, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def deaths(self, request, pk=None):
        round = self.get_object()
        deaths = round.death_set.all()
        serializer = DeathSerializer(deaths, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def unpauses(self, request, pk=None):
        round = self.get_object()
        unpauses = round.unpause_set.all()
        serializer = UnpauseSerializer(unpauses, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def ultuses(self, request, pk=None):
        round = self.get_object()
        ultuses = round.ultuse_set.all()
        serializer = UltUseSerializer(ultuses, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def ultgains(self, request, pk=None):
        round = self.get_object()
        ultgains = round.ultgain_set.all()
        serializer = UltGainSerializer(ultgains, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def revives(self, request, pk=None):
        round = self.get_object()
        revives = round.revive_set.all()
        serializer = ReviveSerializer(revives, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def pointgains(self, request, pk=None):
        round = self.get_object()
        pointgains = round.pointgain_set.all()
        serializer = PointGainSerializer(pointgains, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def pointflips(self, request, pk=None):
        round = self.get_object()
        pointflips = round.pointflip_set.all()
        serializer = PointFlipSerializer(pointflips, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def pauses(self, request, pk=None):
        round = self.get_object()
        pauses = round.pause_set.all()
        serializer = PauseSerializer(pauses, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def npcdeaths(self, request, pk=None):
        round = self.get_object()
        npcdeaths = round.npcdeath_set.all()
        serializer = NPCDeathSerializer(npcdeaths, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def kills(self, request, pk=None):
        round = self.get_object()
        kills = round.kill_set.all()
        serializer = KillSerializer(kills, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def killnpcs(self, request, pk=None):
        round = self.get_object()
        killnpcs = round.killnpc_set.all()
        serializer = KillNPCSerializer(killnpcs, many=True)
        return Response(serializer.data)


class SwitchViewSet(viewsets.ModelViewSet):
    model = Switch
    queryset = Switch.objects.all()
    serializer_class = SwitchSerializer


class DeathViewSet(viewsets.ModelViewSet):
    model = Death
    queryset = Switch.objects.all()
    serializer_class = DeathSerializer


class NPCDeathViewSet(viewsets.ModelViewSet):
    model = NPCDeath
    queryset = NPCDeath.objects.all()
    serializer_class = NPCDeathSerializer


class PauseViewSet(viewsets.ModelViewSet):
    model = Pause
    queryset = Pause.objects.all()
    serializer_class = PauseSerializer


class UnpauseViewSet(viewsets.ModelViewSet):
    model = Unpause
    queryset = Unpause.objects.all()
    serializer_class = UnpauseSerializer


class KillViewSet(viewsets.ModelViewSet):
    model = Kill
    queryset = Kill.objects.all()
    serializer_class = KillSerializer


class ReviveViewSet(viewsets.ModelViewSet):
    model = Revive
    queryset = Revive.objects.all()
    serializer_class = ReviveSerializer


class UltGainViewSet(viewsets.ModelViewSet):
    model = UltGain
    queryset = UltGain.objects.all()
    serializer_class = UltGainSerializer


class UltUseViewSet(viewsets.ModelViewSet):
    model = UltUse
    queryset = UltUse.objects.all()
    serializer_class = UltUseSerializer


class PointGainViewSet(viewsets.ModelViewSet):
    model = PointGain
    queryset = PointGain.objects.all()
    serializer_class = PointGainSerializer


class PointFlipViewSet(viewsets.ModelViewSet):
    model = PointFlip
    queryset = PointFlip.objects.all()
    serializer_class = PointFlipSerializer


class KillNPCViewSet(viewsets.ModelViewSet):
    model = KillNPC
    queryset = KillNPC.objects.all()
    serializer_class = KillNPCSerializer
