from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from . import serializers
from . import models


class TeamColorViewSet(viewsets.ViewSet):
    def list(self, request):
        choices = [{'id': x[0], 'name': x[1]} for x in models.TeamParticipation.COLOR_CHOICES]
        return Response(choices)


class SideViewSet(viewsets.ViewSet):
    def list(self, request):
        choices = [{'id': x[0], 'name': x[1]} for x in models.SIDE_CHOICES if x[0] != 'N']
        return Response(choices)


class HeroViewSet(viewsets.ModelViewSet):
    model = models.Hero
    queryset = models.Hero.objects.all()
    serializer_class = serializers.HeroSerializer

    @detail_route(methods=['get'])
    def damaging_abilities(self, request, pk=None):
        hero = self.get_object()
        abilities = hero.ability_set.filter(damaging_ability=True).all()
        serializer = serializers.AbilitySerializer(abilities, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def reviving_abilities(self, request, pk=None):
        hero = self.get_object()
        abilities = hero.ability_set.filter(revive_ability=True).all()
        serializer = serializers.AbilitySerializer(abilities, many=True)
        return Response(serializer.data)


class MapViewSet(viewsets.ModelViewSet):
    model = models.Map
    queryset = models.Map.objects.all()
    serializer_class = serializers.MapSerializer


class NPCViewSet(viewsets.ModelViewSet):
    model = models.NPC
    queryset = models.NPC.objects.all()
    serializer_class = serializers.NPCSerializer


class TeamViewSet(viewsets.ModelViewSet):
    model = models.Team
    queryset = models.Team.objects.all()
    serializer_class = serializers.TeamSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    model = models.Player
    queryset = models.Player.objects.all()
    serializer_class = serializers.PlayerSerializer


class EventViewSet(viewsets.ModelViewSet):
    model = models.Event
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer

    @detail_route(methods=['get'])
    def matches(self, request, pk=None):
        event = self.get_object()
        matches = event.match_set.prefetch_related('teams').all()
        serializer = serializers.MatchSerializer(matches, many=True)
        return Response(serializer.data)


class MatchViewSet(viewsets.ModelViewSet):
    model = models.Match
    queryset = models.Match.objects.all()
    serializer_class = serializers.MatchSerializer

    @detail_route(methods=['get'])
    def games(self, request, pk=None):
        match = self.get_object()
        games = match.game_set.all()
        serializer = serializers.GameSerializer(games, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def teams(self, request, pk=None):
        match = self.get_object()
        teams = match.teams.all()
        serializer = serializers.TeamSerializer(teams, many=True)
        return Response(serializer.data)


class GameViewSet(viewsets.ModelViewSet):
    model = models.Game
    queryset = models.Game.objects.all()
    serializer_class = serializers.GameSerializer

    @detail_route(methods=['get'])
    def rounds(self, request, pk=None):
        game = self.get_object()
        rounds = game.round_set.all()
        serializer = serializers.RoundSerializer(rounds, many=True)
        return Response(serializer.data)


class RoundViewSet(viewsets.ModelViewSet):
    model = models.Round
    queryset = models.Round.objects.all()
    serializer_class = serializers.RoundSerializer

    @detail_route(methods=['get'])
    def players(self, request, pk=None):
        round = self.get_object()
        game = round.game
        data = {}
        data['left_team'] = [{'id': x.id, 'name': x.name} for x in game.left_team.players.all()]
        data['right_team'] = [{'id': x.id, 'name': x.name} for x in game.right_team.players.all()]
        return Response(data)

    @detail_route(methods=['get'])
    def hero_at_time(self, request, pk=None):
        player = int(request.GET.get('player_id', 0))
        time_point = int(request.GET.get('time_point', 0))
        round = self.get_object()
        switches = round.switch_set.all()
        print(player, time_point)
        if player:
            switches = switches.filter(player__id=player)
            hero = None
            for s in switches:
                if s.time_point > time_point:
                    break
                hero = s.new_hero
                print(hero)
            if hero:
                serializer = serializers.HeroSerializer(hero)
                return Response(serializer.data)
        return Response(None)

    @detail_route(methods=['get'])
    def ult_at_time(self, request, pk=None):
        player = int(request.GET.get('player_id', 0))
        if not player:
            return Response(False)
        time_point = int(request.GET.get('time_point', 0))
        round = self.get_object()
        ultgains = round.ultgain_set.filter(player__id=player).all()
        if not ultgains:
            return Response(False)
        ultuses = round.ultuse_set.filter(player__id=player).all()
        last_gain = 0
        for ug in ultgains:
            if ug.time_point > time_point:
                break
            last_gain = ug.time_point
        if last_gain == 0:
            return Response(False)
        last_use = 0
        for uu in ultuses:
            if uu.time_point > time_point:
                break
            last_use = uu.time_point
        if last_use >= last_gain:
            return Response(False)
        switches = round.switch_set.filter(player__id=player).all()
        last_switch = 0
        for s in switches:
            if s.time_point > time_point:
                break
            last_switch = s.time_point
        if last_switch > last_gain:
            return Response(False)
        return Response(True)

    @detail_route(methods=['get'])
    def switches(self, request, pk=None):
        round = self.get_object()
        switches = round.switch_set.all()
        serializer = serializers.SwitchDisplaySerializer(switches, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def deaths(self, request, pk=None):
        round = self.get_object()
        deaths = round.death_set.all()
        serializer = serializers.DeathDisplaySerializer(deaths, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def unpauses(self, request, pk=None):
        round = self.get_object()
        unpauses = round.unpause_set.all()
        serializer = serializers.UnpauseSerializer(unpauses, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def ultuses(self, request, pk=None):
        round = self.get_object()
        ultuses = round.ultuse_set.all()
        serializer = serializers.UltUseDisplaySerializer(ultuses, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def ultgains(self, request, pk=None):
        round = self.get_object()
        ultgains = round.ultgain_set.all()
        serializer = serializers.UltGainDisplaySerializer(ultgains, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def revives(self, request, pk=None):
        round = self.get_object()
        revives = round.revive_set.all()
        serializer = serializers.ReviveDisplaySerializer(revives, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def pointgains(self, request, pk=None):
        round = self.get_object()
        pointgains = round.pointgain_set.all()
        serializer = serializers.PointGainSerializer(pointgains, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def pointflips(self, request, pk=None):
        round = self.get_object()
        pointflips = round.pointflip_set.all()
        serializer = serializers.PointFlipSerializer(pointflips, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def pauses(self, request, pk=None):
        round = self.get_object()
        pauses = round.pause_set.all()
        serializer = serializers.PauseSerializer(pauses, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def npcdeaths(self, request, pk=None):
        round = self.get_object()
        npcdeaths = round.npcdeath_set.all()
        serializer = serializers.NPCDeathDisplaySerializer(npcdeaths, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def kills(self, request, pk=None):
        round = self.get_object()
        kills = round.kill_set.all()
        serializer = serializers.KillDisplaySerializer(kills, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def killnpcs(self, request, pk=None):
        round = self.get_object()
        killnpcs = round.killnpc_set.all()
        serializer = serializers.KillNPCDisplaySerializer(killnpcs, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def overtimestarts(self, request, pk=None):
        round = self.get_object()
        overtimestarts = round.overtimestart_set.all()
        serializer = serializers.OvertimeStartSerializer(overtimestarts, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def replaystarts(self, request, pk=None):
        round = self.get_object()
        replaystarts = round.replaystart_set.all()
        serializer = serializers.ReplayStartSerializer(replaystarts, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def replayends(self, request, pk=None):
        round = self.get_object()
        replayends = round.replayend_set.all()
        serializer = serializers.ReplayEndSerializer(replayends, many=True)
        return Response(serializer.data)


class SwitchViewSet(viewsets.ModelViewSet):
    model = models.Switch
    queryset = models.Switch.objects.all()
    serializer_class = serializers.SwitchSerializer


class DeathViewSet(viewsets.ModelViewSet):
    model = models.Death
    queryset = models.Death.objects.all()
    serializer_class = serializers.DeathSerializer


class NPCDeathViewSet(viewsets.ModelViewSet):
    model = models.NPCDeath
    queryset = models.NPCDeath.objects.all()
    serializer_class = serializers.NPCDeathSerializer


class PauseViewSet(viewsets.ModelViewSet):
    model = models.Pause
    queryset = models.Pause.objects.all()
    serializer_class = serializers.PauseSerializer


class UnpauseViewSet(viewsets.ModelViewSet):
    model = models.Unpause
    queryset = models.Unpause.objects.all()
    serializer_class = serializers.UnpauseSerializer


class ReplayStartViewSet(viewsets.ModelViewSet):
    model = models.ReplayStart
    queryset = models.ReplayStart.objects.all()
    serializer_class = serializers.ReplayStartSerializer


class ReplayEndViewSet(viewsets.ModelViewSet):
    model = models.ReplayEnd
    queryset = models.ReplayEnd.objects.all()
    serializer_class = serializers.ReplayEndSerializer


class OvertimeStartViewSet(viewsets.ModelViewSet):
    model = models.OvertimeStart
    queryset = models.OvertimeStart.objects.all()
    serializer_class = serializers.OvertimeStartSerializer


class KillViewSet(viewsets.ModelViewSet):
    model = models.Kill
    queryset = models.Kill.objects.all()
    serializer_class = serializers.KillSerializer


class ReviveViewSet(viewsets.ModelViewSet):
    model = models.Revive
    queryset = models.Revive.objects.all()
    serializer_class = serializers.ReviveSerializer


class UltGainViewSet(viewsets.ModelViewSet):
    model = models.UltGain
    queryset = models.UltGain.objects.all()
    serializer_class = serializers.UltGainSerializer


class UltUseViewSet(viewsets.ModelViewSet):
    model = models.UltUse
    queryset = models.UltUse.objects.all()
    serializer_class = serializers.UltUseSerializer


class PointGainViewSet(viewsets.ModelViewSet):
    model = models.PointGain
    queryset = models.PointGain.objects.all()
    serializer_class = serializers.PointGainSerializer


class PointFlipViewSet(viewsets.ModelViewSet):
    model = models.PointFlip
    queryset = models.PointFlip.objects.all()
    serializer_class = serializers.PointFlipSerializer


class KillNPCViewSet(viewsets.ModelViewSet):
    model = models.KillNPC
    queryset = models.KillNPC.objects.all()
    serializer_class = serializers.KillNPCSerializer
