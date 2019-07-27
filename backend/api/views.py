from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache

from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters

from rest_framework import pagination, status

import django
from django.db.models import Q
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.reverse_related import ForeignObjectRel, OneToOneRel
from decimal import Decimal
from . import serializers
from . import models
from .utils import lookup_team, match_up_players
from django.contrib.auth.models import User, AnonymousUser

# Serve Vue Application
index_view = never_cache(TemplateView.as_view(template_name='index.html'))


class UserViewSet(viewsets.ModelViewSet):
    model = User
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def create(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def list(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        users = User.objects.all()
        return Response(self.serializer_class(users, many=True).data)

    @action(methods=['get'], detail=False)
    def current_user(self, request):
        #print(dir(request))
        #print(request.auth)
        #print(request.data)
        #print(request.user)
        if isinstance(request.user, AnonymousUser):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(self.serializer_class(request.user).data)

class RelatedOrderingFilter(filters.OrderingFilter):
    """

    See: https://github.com/tomchristie/django-rest-framework/issues/1005

    Extends OrderingFilter to support ordering by fields in related models
    using the Django ORM __ notation
    """

    def is_valid_field(self, model, field):
        """
        Return true if the field exists within the model (or in the related
        model specified using the Django ORM __ notation)
        """
        components = field.split('__', 1)
        try:
            field = model._meta.get_field(components[0])

            if isinstance(field, OneToOneRel):
                return self.is_valid_field(field.related_model, components[1])

            # reverse relation
            if isinstance(field, ForeignObjectRel):
                return self.is_valid_field(field.model, components[1])

            # foreign key
            if field.remote_field and len(components) == 2:
                return self.is_valid_field(field.related_model, components[1])
            return True
        except FieldDoesNotExist:
            return False

    def remove_invalid_fields(self, queryset, fields, ordering, view):
        return [term for term in fields
                if self.is_valid_field(queryset.model, term.lstrip('-'))]


class TrainInfoViewSet(viewsets.ViewSet):
    def list(self, request):
        max_heroes = 50
        max_labels = 250
        max_maps = 40
        max_spectator_modes = 20
        max_statuses = 15
        heroes = models.Hero.objects.order_by('id').prefetch_related('npc_set').prefetch_related('abilities').all()
        maps = models.Map.objects.order_by('id').all()
        map_modes = [x[1].lower() for x in models.Map.MODE_CHOICES]
        colors = [x[1].lower() for x in models.TeamParticipation.COLOR_CHOICES]
        statuses = models.Status.objects.order_by('id').all()
        spectator_modes = [x[1].lower() for x in models.Event.SPECTATOR_MODE_CHOICES]
        npcs = []
        labels = []
        for c in colors:
            labels.append(c)
        for h in heroes:
            labels.append(h.name.lower())
            labels.append(h.name.lower() + '_assist')
            for a in h.abilities.all():
                name = a.name.lower()
                if a.damaging_ability or a.revive_ability or name == 'defense matrix':
                    if name not in labels:
                        labels.append(name)
                    headshot_name = name + ' headshot'
                    if a.headshot_capable and headshot_name not in labels:
                        labels.append(headshot_name)
            for n in h.npc_set.all():
                npcs.append(n.name.lower())
                labels.append(n.name.lower() + '_npc')
        heroes = [x.name.lower() for x in heroes]
        while len(heroes) < max_heroes:
            heroes.append('')

        while len(labels) < max_labels:
            labels.append('')

        maps = [x.name.lower() for x in maps]
        while len(maps) < max_maps:
            maps.append('')

        while len(spectator_modes) < max_spectator_modes:
            spectator_modes.append('')
        statuses = [x.name.lower() for x in statuses]
        while len(statuses) < max_statuses:
            statuses.append('')
        data = {
            'heroes': heroes,
            'map_modes': map_modes,
            'maps': maps,
            'npcs': npcs,
            'statuses': statuses,
            'colors': colors,
            'spectator_modes': spectator_modes,
            'kill_feed_labels': labels
        }
        for k, v in data.items():
            print(k, len(v))
        return Response(data)


class TeamColorViewSet(viewsets.ViewSet):
    def list(self, request):
        choices = [{'id': x[0], 'name':x[1]} for x in models.TeamParticipation.COLOR_CHOICES]
        return Response(choices)


class MapModeViewSet(viewsets.ViewSet):
    def list(self, request):
        choices = [x[1] for x in models.Map.MODE_CHOICES]
        return Response(choices)


class FilmFormatViewSet(viewsets.ViewSet):
    def list(self, request):
        choices = [{'id': x[0], 'name': x[1]} for x in models.StreamVod.FILM_FORMAT_CHOICES]
        return Response(choices)


class SideViewSet(viewsets.ViewSet):
    def list(self, request):
        choices = [{'id': x[0], 'name': x[1]} for x in models.SIDE_CHOICES]
        return Response(choices)


class SpectatorModeViewSet(viewsets.ViewSet):
    def list(self, request):
        choices = [{'id': x[0], 'name': x[1]} for x in models.Event.SPECTATOR_MODE_CHOICES]
        return Response(choices)


class AnnotationChoiceViewSet(viewsets.ViewSet):
    def list(self, request):
        choices = [{'id': x[0], 'name': x[1]} for x in models.Round.ANNOTATION_CHOICES]
        return Response(choices)


class VodStatusChoiceViewSet(viewsets.ViewSet):
    def list(self, request):
        choices = [{'id': x[0], 'name': x[1]} for x in models.StreamVod.STATUS_CHOICES]
        return Response(choices)


class VodTypeChoiceViewSet(viewsets.ViewSet):
    def list(self, request):
        choices = [{'id': x[0], 'name': x[1]} for x in models.StreamVod.TYPE_CHOICES]
        return Response(choices)


class HeroViewSet(viewsets.ModelViewSet):
    model = models.Hero
    queryset = models.Hero.objects.all()
    serializer_class = serializers.HeroAbilitySerializer

    @action(methods=['get'], detail=False)
    def training_hero_list(self, request):
        queryset = models.Hero.objects.order_by('id')
        return Response(self.serializer_class(queryset, many=True).data)


class StatusEffectChoiceViewSet(viewsets.ModelViewSet):
    model = models.Status
    queryset = models.Status.objects.all()
    serializer_class = serializers.StatusSerializer


class HeroSummaryViewSet(viewsets.ModelViewSet):
    model = models.Hero
    queryset = models.Hero.objects.all()
    serializer_class = serializers.HeroSummarySerializer


class AbilityViewSet(viewsets.ModelViewSet):
    model = models.Ability
    queryset = models.Ability.objects.all()
    serializer_class = serializers.AbilitySerializer

    @action(methods=['get'], detail=False)
    def damaging_abilities(self, request):
        abilities = models.Ability.objects.filter(damaging_ability=True).all()
        serializer = serializers.AbilitySerializer(abilities, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def reviving_abilities(self, request):
        abilities = models.Ability.objects.filter(revive_ability=True).all()
        serializer = serializers.AbilitySerializer(abilities, many=True)
        return Response(serializer.data)


class MapViewSet(viewsets.ModelViewSet):
    model = models.Map
    queryset = models.Map.objects.all()
    serializer_class = serializers.MapSerializer

    @action(methods=['get'], detail=False)
    def training_map_list(self, request):
        queryset = models.Map.objects.order_by('id')
        return Response(self.serializer_class(queryset, many=True).data)


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

    @action(methods=['get'], detail=True)
    def matches(self, request, pk=None):
        event = self.get_object()
        matches = event.match_set.prefetch_related('teams').all()
        serializer = serializers.MatchSerializer(matches, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def vods(self, request, pk=None):
        event = self.get_object()
        start_date = event.start_date
        end_date = event.end_date
        vods =[]
        for c in event.stream_channels.prefetch_related('streamvod_set').all():
            for v in c.streamvod_set.all():
                if start_date and v.broadcast_date.date() < start_date:
                    continue
                if end_date and v.broadcast_date.date() > end_date:
                    continue
                vods.append(v)
        return Response(serializers.StreamVodSerializer(vods, many=True).data)

    @action(methods=['get'], detail=True)
    def available_vods(self, request, pk=None):
        import requests
        import datetime
        event = self.get_object()
        start_date = event.start_date
        end_date = event.end_date
        vods =[]
        for c in event.stream_channels.prefetch_related('streamvod_set').all():
            cursor = ''
            if c.site == 'T':
                response = requests.get('https://api.twitch.tv/helix/users?login={}'.format(c.name),
                                        headers={'Client-ID': 'fgjp7t0f365uazgs84n7t9xhf19xt2'})
                data = response.json()['data'][0]
                id = data['id']
                key = 'fgjp7t0f365uazgs84n7t9xhf19xt2'
                break_early = False
                while True:
                    vod_urls = [x.url for x in c.streamvod_set.all()]
                    if not cursor:
                        response = requests.get('https://api.twitch.tv/helix/videos?user_id={}'.format(id),
                                                headers={'Client-ID': key})
                    else:
                        response = requests.get(
                            'https://api.twitch.tv/helix/videos?user_id={}&first=100&after={}'.format(id, cursor),
                            headers={'Client-ID': key})

                    data = response.json()
                    if 'data' not in data:
                        print(data)
                        break
                    for v in data['data']:
                        if v['published_at'] is None:
                            continue
                        published_at = datetime.datetime.strptime(v['published_at'], '%Y-%m-%dT%H:%M:%SZ').date()
                        if event.channel_query_string is not None and event.channel_query_string not in v['title']:
                            continue
                        if end_date is not None:
                            if published_at > end_date:
                                continue
                        if start_date is not None:
                            if published_at < start_date:
                                break_early = True
                                break
                        url = v['url']
                        if url in vod_urls:
                            continue
                        v['channel'] = c.id
                        v['channel_title'] = c.name
                        v['channel_type'] = 'Twitch'
                        vods.append(v)
                        vod_urls.append(url)
                    if break_early:
                        break
                    try:
                        cursor = data['pagination']['cursor']
                    except KeyError:
                        break
            elif c.site == 'Y':
                key = 'AIzaSyB87s7SK8p7mniHYnDB7xbkWtQg1G-EAM8'
                while True:
                    vod_urls = [x.url for x in c.streamvod_set.all()]
                    if not cursor:
                        url = 'https://www.googleapis.com/youtube/v3/search?key={}&channelId={}&part=snippet,id&order=date&maxResults=50'.format(key, c.youtube_channel_id)
                        response = requests.get(url)
                    else:
                        url = 'https://www.googleapis.com/youtube/v3/search?key={}&channelId={}&part=snippet,id&order=date&maxResults=50&pageToken={}'.format(key, c.youtube_channel_id, cursor)

                        response = requests.get(url)
                    data = response.json()
                    print(data)
                    for item in data['items']:
                        try:
                            url = 'https://www.youtube.com/watch?v=' + item['id']['videoId']
                        except KeyError:
                            continue
                        if url in vod_urls:
                            continue
                        v = {'url': url,
                             'title': item['snippet']['title'],
                             'published_at': item['snippet']['publishedAt'],
                             'channel': c.id,
                             'channel_title': c.name,
                             'channel_type': 'YouTube'
                             }
                        vods.append(v)
                        vod_urls.append(url)
                    try:
                        cursor= data['nextPageToken']
                    except KeyError:
                        break
        return Response(vods)


class MatchViewSet(viewsets.ModelViewSet):
    model = models.Match
    queryset = models.Match.objects.all()
    serializer_class = serializers.MatchSerializer

    @action(methods=['get'], detail=True)
    def games(self, request, pk=None):
        match = self.get_object()
        games = match.game_set.all()
        serializer = serializers.GameSerializer(games, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def teams(self, request, pk=None):
        match = self.get_object()
        teams = match.teams.all()
        serializer = serializers.TeamSerializer(teams, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.vod = request.data['vod']
        instance.film_format = request.data['film_format']
        diff = Decimal(round(float(instance.start_time) - request.data['start_time'], 1))
        print(diff)
        if abs(diff) > 1:
            rounds = models.Round.objects.filter(game__match=instance).all()
            for r in rounds:
                r.begin -= diff
                r.end -= diff
                r.save()

        instance.save()
        return Response()


class GameViewSet(viewsets.ModelViewSet):
    model = models.Game
    queryset = models.Game.objects.all()
    serializer_class = serializers.GameSerializer

    def create(self, request, *args, **kwargs):
        match = models.Match.objects.get(id=request.data['match'])
        game_num = int(request.data['game_number'])
        try:
            game = models.Game.objects.get(game_number=game_num, match=match)
            return Response('Game already exists for this match.',status=status.HTTP_409_CONFLICT)
        except models.Game.DoesNotExist:
            pass

        if 'left_team' in request.data:
            print(request.data)
            left_team_participation = models.TeamParticipation.objects.create(team_id=request.data['left_team'], color='B')
            do_subtract = min([int(i) for i in request.data['left_players'].keys()]) == 1
            for i, p in request.data['left_players'].items():
                if do_subtract:
                    i -= 1
                pp = models.PlayerParticipation.objects.create(team_participation=left_team_participation, player_id=p,
                                                               player_index=int(i))

            right_team_participation = models.TeamParticipation.objects.create(team_id=request.data['right_team'], color='R')
            for i, p in request.data['right_players'].items():
                if do_subtract:
                    i -= 1
                pp = models.PlayerParticipation.objects.create(team_participation=right_team_participation, player_id=p,
                                                               player_index=int(i))
        else:
            teams = match.teams.all()
            left_team_participation = models.TeamParticipation.objects.create(team=teams[0], color='B')
            for i, p in enumerate(teams[0].players.all()):
                pp = models.PlayerParticipation.objects.create(player=p,
                                                               team_participation=left_team_participation,
                                                               player_index=i)
                if i == 5:
                    break
            right_team_participation = models.TeamParticipation.objects.create(team=teams[1], color='R')
            for i, p in enumerate(teams[1].players.all()):
                pp = models.PlayerParticipation.objects.create(player=p,
                                                               team_participation=right_team_participation,
                                                               player_index=i)
                if i == 5:
                    break
        game = models.Game.objects.create(match=match,
                                          game_number=int(request.data['game_number']), map_id=request.data['map'],
                                          left_team=left_team_participation, right_team=right_team_participation)
        return Response(self.serializer_class(game).data)

    @action(methods=['post'], detail=False)
    def create_upload(self, request, *args, **kwargs):
        for k, v in request.data.items():
            if k == 'rounds':
                continue
            print(k, v)
        vod = models.StreamVod.objects.get(id=int(request.data['vod_id']))
        #if vod.round_set.count() > 0:
        #    return Response()
        print(vod)
        channel = vod.channel
        event, _ = models.Event.objects.get_or_create(name=request.data['event'].lower())
        if event.channel != channel:
            event.channel = channel
            event.save()
        create_match = True
        matches = event.match_set.filter(description=request.data['description']).all()
        for m in matches:
            #has_manual = False
            #for g in m.game_set.all():
            #    if g.round_set.filter(annotation_status='M').exists():
            #        has_manual = True
            #if not has_manual:
            #    m.delete()
            #    continue
            teams = m.teams.all()
            team_one_found = False
            team_two_found = False
            for t in teams:
                if t.name.lower() == request.data['team_one'].lower():
                    team_one_found = True
                elif t.name.lower() == request.data['team_two'].lower():
                    team_two_found = True
            if team_one_found and team_two_found:
                match = m
                create_match = False
        if create_match:
            match = models.Match.objects.create(event=event, description=request.data['description'])
        left_names = {}
        right_names = {}
        r =request.data['rounds'][0]
        print(r['round']['map'])
        left_color = r['left_color']
        right_color = r['right_color']
        map_object = models.Map.objects.get(name__iexact=r['round']['map'])
        print(map_object)
        if map_object is None:
            error
        for p, v in r['player'].items():
            s, i = p.split('_')
            if s == 'left':
                left_names[i] = v['player_name']
            else:
                right_names[i] = v['player_name']
        team_one = models.Team.objects.filter(name__iexact=request.data['team_one']).first()
        team_two = models.Team.objects.filter(name__iexact=request.data['team_two']).first()
        if team_one is None:
            team_one = models.Team.objects.create(name=request.data['team_one'].lower())
        team_one_players = team_one.players.all()
        if not team_one_players:
            team_one_player_names = lookup_team(request.data['team_one'])
            print(team_one_player_names)
            for p in team_one_player_names:
                print(p)
                player = models.Player.objects.filter(name=p.lower()).first()
                if player is None:
                    player = models.Player.objects.create(name=p.lower())
                affiliation = models.Affiliation.objects.create(team=team_one, player=player)
        team_one_players = team_one.players.all()
        if team_two is None:
            team_two = models.Team.objects.create(name=request.data['team_two'].lower())
        team_two_players = team_two.players.all()
        if not team_two_players:
            team_two_player_names = lookup_team(request.data['team_two'])
            for p in team_two_player_names:
                player = models.Player.objects.filter(name=p.lower()).first()
                if player is None:
                    player = models.Player.objects.create(name=p.lower())
                affiliation = models.Affiliation.objects.create(team=team_two, player=player)
        print(team_two.affiliation_set.all())
        team_two_players = team_two.players.all()
        if create_match:
            match.teams.add(team_one)
            match.teams.add(team_two)
            match.save()
        print('left_names', left_names)
        print('right_names', right_names)
        print(team_one_players, team_two_players)
        print(team_one.id, team_two.id)
        team_one_players, team_two_players, one_left = match_up_players(left_names, right_names, team_one_players, team_two_players)

        print(team_one_players, team_two_players)
        if one_left:
            left_team = team_one
            left_team_players = team_one_players
            right_team = team_two
            right_team_players = team_two_players
        else:
            left_team = team_two
            left_team_players = team_two_players
            right_team = team_one
            right_team_players = team_one_players
        try:
            game = models.Game.objects.get(match=match,game_number=int(request.data['game_number']))
        except models.Game.DoesNotExist:
            left_team_participation = models.TeamParticipation.objects.create(team=left_team, color='B')
            for i, p in left_team_players.items():
                pp = models.PlayerParticipation.objects.create(team_participation=left_team_participation, player=p, player_index=int(i))

            right_team_participation = models.TeamParticipation.objects.create(team=right_team, color='R')
            for i, p in right_team_players.items():
                pp = models.PlayerParticipation.objects.create(team_participation=right_team_participation, player=p,
                                                               player_index=int(i))

            game = models.Game.objects.create(match=match,game_number=int(request.data['game_number']), map=map_object, left_team=left_team_participation, right_team=right_team_participation)
        errors = []
        error_log_path = r'E:\Data\Overwatch\issues_vod.txt'
        print(len(request.data['rounds']), 'total rounds')
        for i, r in enumerate(request.data['rounds']):
            print('Round', i)
            r_data = r['round']
            attacking_side = 'N'
            if r_data['attacking_color'] == 'blue':
                attacking_side = 'L'
            elif r_data['attacking_color'] == 'red':
                attacking_side = 'R'
            try:
                instance = models.Round.objects.get(game=game, round_number=i+1)
                created = False
            except models.Round.DoesNotExist:
                instance = models.Round.objects.create(stream_vod=vod, game=game, round_number=i+1, attacking_side=attacking_side, begin=r_data['begin'], end=r_data['end'])
                created = True
            print(instance, created)
            if not created:
                continue
            instance.ultgain_set.all().delete()
            instance.ultuse_set.all().delete()
            instance.replaystart_set.all().delete()
            instance.replayend_set.all().delete()
            switches = []
            ult_gains = []
            ult_uses = []
            if 'replays' in r:
                replay_begins = []
                replay_ends = []
                for replay in r['replays']:
                    replay_begins.append(models.ReplayStart(round=instance, time_point=replay['begin']))
                    replay_ends.append(models.ReplayEnd(round=instance, time_point=replay['end']))
                models.ReplayStart.objects.bulk_create(replay_begins)
                models.ReplayEnd.objects.bulk_create(replay_ends)

            if 'pauses' in r:
                pauses = []
                unpauses = []
                for p in r['pauses']:
                    pauses.append(models.Pause(round=instance, time_point=p['begin']))
                    unpauses.append(models.Unpause(round=instance, time_point=p['end']))
                models.Pause.objects.bulk_create(pauses)
                models.Unpause.objects.bulk_create(unpauses)

            if 'small_windows' in r:
                smaller_window_starts = []
                smaller_window_ends = []
                for p in r['small_windows']:
                    smaller_window_starts.append(models.SmallerWindowStart(round=instance, time_point=p['begin']))
                    smaller_window_ends.append(models.SmallerWindowEnd(round=instance, time_point=p['end']))
                models.SmallerWindowStart.objects.bulk_create(smaller_window_starts)
                models.SmallerWindowEnd.objects.bulk_create(smaller_window_ends)
            sequences = instance.sequences
            for k, v in r['player'].items():
                side, num = k.split('_')
                if side == 'left':
                    p = left_team_players[num]
                else:
                    p = right_team_players[num]
                for i, s in enumerate(v['switches']):
                    for seq in sequences:
                        if seq[0] <= s[0] <= seq[1]:
                            break
                    else:
                        continue
                    hero = models.Hero.objects.get(name__iexact=s[1])
                    if i < len(v['switches']) - 1:
                        switches.append(models.Switch(round=instance, player=p, new_hero=hero, time_point=s[0], end_time_point=v['switches'][i+1][0]))
                    else:
                        switches.append(models.Switch(round=instance, player=p, new_hero=hero, time_point=s[0]))
                for ug in v['ult_gains']:
                    for seq in sequences:
                        if isinstance(ug, list):
                            ug = ug[0]
                        if seq[0] <= ug <= seq[1]:
                            break
                    else:
                        continue
                    ult_gains.append(models.UltGain(player=p, round=instance, time_point=ug))
                for uu in v['ult_uses']:
                    for seq in sequences:
                        if isinstance(uu, list):
                            uu = uu[0]
                        if seq[0] <= uu <= seq[1]:
                            break
                    else:
                        continue
                    ult_uses.append(models.UltUse(player=p, round=instance, time_point=uu))
            models.Switch.objects.bulk_create(switches)
            models.UltGain.objects.bulk_create(ult_gains)
            models.UltUse.objects.bulk_create(ult_uses)

            instance.kill_set.all().delete()
            instance.killnpc_set.all().delete()
            instance.death_set.all().delete()
            instance.npcdeath_set.all().delete()
            instance.revive_set.all().delete()

            revives = []
            deaths = []
            npcdeaths = []
            kills = []
            killnpcs = []
            for event in r['kill_feed']:
                time_point = round(event['time_point'], 1)
                for seq in sequences:
                    if seq[0] <= time_point <= seq[1]:
                        break
                else:
                    continue

                event = event['event']
                if event['ability'] == 'resurrect':
                    if event['first_color'] == left_color:
                        side = 'left'
                    else:
                        side = 'right'
                    reviving_player = instance.get_player_of_hero(event['first_hero'], time_point, side)
                    revived_player = instance.get_player_of_hero(event['second_hero'], time_point, side)
                    if reviving_player is None:
                        errors.append((instance.id, time_point, 'revive', event['first_hero'], side))
                        continue
                    if revived_player is None:
                        errors.append((instance.id, time_point, 'revive', event['second_hero'], side))
                        continue
                    ability = models.Ability.objects.get(name='Resurrect')
                    revives.append(
                        models.Revive(reviving_player=reviving_player, revived_player=revived_player, round=instance,
                                      time_point=time_point, ability=ability))
                elif event['first_hero'] == 'n/a':
                    # death
                    if event['second_color'] == left_color:
                        side = 'left'
                    else:
                        side = 'right'
                    try:
                        npc = models.NPC.objects.get(name__iexact=event['second_hero'])
                        npcdeaths.append(
                            models.NPCDeath(round=instance, time_point=time_point, npc=npc, side=side[0].upper()))
                    except models.NPC.DoesNotExist:
                        # Hero death
                        dying_player = instance.get_player_of_hero(event['second_hero'], time_point, side)
                        if dying_player is None:
                            errors.append((instance.id, time_point, 'death', event['second_hero'], side))
                            continue
                        deaths.append(models.Death(round=instance, time_point=time_point, player=dying_player))
                else:
                    # kills
                    if event['second_color'] == left_color:
                        killing_side = 'right'
                        killed_side = 'left'
                    else:
                        killing_side = 'left'
                        killed_side = 'right'
                    killing_player = instance.get_player_of_hero(event['first_hero'], time_point, killing_side)
                    if killing_player is None:
                        errors.append((instance.id, time_point, 'kill', event['first_hero'], killing_side))
                        continue
                    hero = models.Hero.objects.get(name__iexact=event['first_hero'])
                    if 'headshot' not in event:
                        headshot = event['ability'].endswith('headshot')
                    else:
                        headshot = event['headshot']
                    ability = event['ability'].replace(' headshot', '')
                    ability = hero.abilities.filter(name__iexact=ability).first()
                    assists = []
                    for a in event['assists']:
                        hero = models.Hero.objects.get(name__iexact=a.replace('_assist', ''))
                        assists.append(hero.name)

                    print(assists)
                    try:
                        npc = models.NPC.objects.get(name__iexact=event['second_hero'])
                        if ability is not None:
                            if not assists:
                                killnpcs.append(
                                models.KillNPC(round=instance, time_point=time_point, killing_player=killing_player,
                                               killed_npc=npc, ability=ability))
                                npcdeaths.append(models.NPCDeath(round=instance, time_point=time_point, npc=npc,
                                                                 side=killed_side[0].upper()))
                            else:
                                m = models.KillNPC.objects.create(round=instance, time_point=time_point, killing_player=killing_player,
                                               killed_npc=npc, ability=ability)
                                for a in assists:
                                    assisting_player = instance.get_player_of_hero(a, time_point, killing_side)
                                    if assisting_player is None:
                                        continue
                                    m.assisting_players.add(assisting_player)
                    except models.NPC.DoesNotExist:
                        killed_player = instance.get_player_of_hero(event['second_hero'], time_point, killed_side)
                        if killed_player is None:
                            errors.append((instance.id, time_point, 'kill', event['second_hero'], killed_side))
                            continue
                        if ability is not None:
                            if not assists:
                                kills.append(
                                models.Kill(round=instance, time_point=time_point, killing_player=killing_player,
                                            killed_player=killed_player, ability=ability, headshot=headshot))
                                deaths.append(models.Death(round=instance, time_point=time_point, player=killed_player))
                            else:
                                m = models.Kill.objects.create(round=instance, time_point=time_point, killing_player=killing_player,
                                            killed_player=killed_player, ability=ability, headshot=headshot)
                                for a in assists:
                                    assisting_player = instance.get_player_of_hero(a, time_point, killing_side)
                                    print('assisting_player', assisting_player)
                                    if assisting_player is None:
                                        continue
                                    m.assisting_players.add(assisting_player)
            print(revives)
            models.Revive.objects.bulk_create(revives)
            print(deaths)
            models.Death.objects.bulk_create(deaths)
            print(npcdeaths)
            models.NPCDeath.objects.bulk_create(npcdeaths)
            print(killnpcs)
            models.KillNPC.objects.bulk_create(killnpcs)
            print(kills)
            models.Kill.objects.bulk_create(kills)
            with open(error_log_path, 'a') as f:
                for e in errors:
                    f.write('{}\n'.format('\t'.join(map(str, e))))
            instance.annotation_status = 'O'
            instance.save()
        return Response()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        print(request.data)
        for c in instance.left_team.COLOR_CHOICES:
            if request.data['left_team']['color'] in c:
                value = c[0]
                break
        instance.map = models.Map.objects.get(id=request.data['map'])
        instance.left_team.color = value
        instance.left_team.save()
        for c in instance.right_team.COLOR_CHOICES:
            if request.data['right_team']['color'] in c:
                value = c[0]
                break
        instance.right_team.color = value
        instance.right_team.save()
        instance.save()
        return Response(self.serializer_class(instance).data)

    @action(methods=['put'], detail=True)
    def update_teams(self, request, pk=None):
        game = self.get_object()
        left_t = models.TeamParticipation.objects.prefetch_related('playerparticipation_set').get(id=request.data['left_team']['id'])
        left_t.color = request.data['left_team']['color']
        for i,p in enumerate(left_t.playerparticipation_set.all()):
            if p.player_id != request.data['left_team']['players'][i]['player']:
                p.player_id = request.data['left_team']['players'][i]['player']
                p.save()
        left_t.save()
        game.left_team = left_t
        right_t = models.TeamParticipation.objects.prefetch_related('playerparticipation_set').get(id=request.data['right_team']['id'])
        right_t.color = request.data['right_team']['color']
        for i,p in enumerate(right_t.playerparticipation_set.all()):
            if p.player_id != request.data['right_team']['players'][i]['player']:
                p.player_id = request.data['right_team']['players'][i]['player']
                p.save()
        right_t.save()
        game.right_team = right_t
        game.save()
        return Response('Success')

    @action(methods=['get'], detail=True)
    def rounds(self, request, pk=None):
        game = self.get_object()
        rounds = game.round_set.all()
        serializer = serializers.RoundSerializer(rounds, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def teams(self, request, pk=None):
        game = self.get_object()
        left = serializers.TeamParticipationSerializer(game.left_team).data
        right = serializers.TeamParticipationSerializer(game.right_team).data
        return Response({'left': left, 'right': right})

class StreamChannelViewSet(viewsets.ModelViewSet):
    model = models.StreamChannel
    queryset = models.StreamChannel.objects.all()
    serializer_class = serializers.StreamChannelSerializer

    @action(methods=['get'], detail=True)
    def vods(self, request, pk=None):
        channel = self.get_object()
        vods = channel.streamvod_set.all()
        return Response(serializers.StreamVodSerializer(vods, many=True).data)

    @action(methods=['get'], detail=True)
    def available_vods(self, request, pk=None):
        import requests
        c = self.get_object()
        if c.site == 'T':
            response = requests.get('https://api.twitch.tv/helix/users?login={}'.format(c.name),
                                    headers={'Client-ID': 'fgjp7t0f365uazgs84n7t9xhf19xt2'})
            data = response.json()['data'][0]
            id = data['id']
            print(id)
            cursor = ''
            vods = []
            while True:
                vod_urls = [x.url for x in c.streamvod_set.all()]
                if not cursor:
                    response = requests.get('https://api.twitch.tv/helix/videos?user_id={}'.format(id),
                                            headers={'Client-ID': 'fgjp7t0f365uazgs84n7t9xhf19xt2'})
                else:
                    response = requests.get(
                        'https://api.twitch.tv/helix/videos?user_id={}&first=100&after={}'.format(id, cursor),
                        headers={'Client-ID': 'fgjp7t0f365uazgs84n7t9xhf19xt2'})

                data = response.json()
                print(data.keys())
                for v in data['data']:
                    url = v['url']
                    if url in vod_urls:
                        continue
                    vods.append(v)
                    vod_urls.append(url)
                try:
                    print(data['pagination'])
                    cursor = data['pagination']['cursor']
                except KeyError:
                    break
        return Response(vods)


class RoundStatusViewSet(viewsets.ModelViewSet):
    model = models.Round
    queryset = models.Round.objects.prefetch_related('game', 'game__match', 'game__match__event').filter(~Q(stream_vod=None)).all()
    serializer_class = serializers.RoundStatusSerializer
    filter_backends = (filters.SearchFilter, RelatedOrderingFilter,)
    pagination_class = pagination.LimitOffsetPagination
    search_fields = ('game__match__event__name', 'game__match__teams__name')

    def list(self, request, *args, **kwargs):
        print(request.query_params)
        return super(RoundStatusViewSet, self).list(request, *args, **kwargs)


class TrainRoundViewSet(viewsets.ModelViewSet):
    model = models.Round
    queryset = models.Round.objects.filter(annotation_status='M').order_by('pk').all()
    serializer_class = serializers.RoundDisplaySerializer


class ExampleRoundViewSet(viewsets.ModelViewSet):
    model = models.Round
    queryset = models.Round.objects.filter(annotation_status='M').order_by('pk').all()
    serializer_class = serializers.RoundDisplaySerializer

    def get_queryset(self):
        queryset = []
        for c in models.StreamVod.FILM_FORMAT_CHOICES:
            r = models.Round.objects.filter(annotation_status='M', stream_vod__film_format=c[0]).order_by('pk').first()
            if r is None:
                continue
            queryset.append(r)
        return queryset


class TrainRoundPlusViewSet(viewsets.ModelViewSet):
    model = models.Round
    queryset = models.Round.objects.filter(
        Q(annotation_status='M') | Q(game__match__event__name='overwatch league - season 1')).order_by('pk').all()
    serializer_class = serializers.RoundDisplaySerializer


class TrainVodViewSet(viewsets.ModelViewSet):
    model = models.StreamVod
    queryset = models.StreamVod.objects.filter(round__annotation_status='M').order_by('pk').all()
    serializer_class = serializers.VodDisplaySerializer


class VodStatusViewSet(viewsets.ModelViewSet):
    model = models.StreamVod
    queryset = models.StreamVod.objects.filter(round__annotation_status='M').order_by('pk').distinct().all()
    serializer_class = serializers.VodStatusSerializer
    filter_backends = (filters.SearchFilter, RelatedOrderingFilter,)
    pagination_class = pagination.LimitOffsetPagination

    def list(self, request, *args, **kwargs):
        print(request.query_params)
        return super(VodStatusViewSet, self).list(request, *args, **kwargs)


class AnnotateVodViewSet(viewsets.ModelViewSet):
    model = models.StreamVod
    queryset = models.StreamVod.objects.all()
    serializer_class = serializers.VodDisplaySerializer

    @action(methods=['get'], detail=False)
    def in_out_game(self, request):
        vods = models.StreamVod.objects.filter(status='N', pk__gte=2290).all()
        return Response(self.serializer_class(vods, many=True).data)

    @action(methods=['post'], detail=False)
    def upload_in_out_game(self, request):
        print(request.data)
        vod = models.StreamVod.objects.get(id=request.data['vod_id'])
        event = None
        for e in vod.channel.events.all():
            if e.start_date is None or e.end_date is None:
                continue

            if vod.broadcast_date.date() < e.start_date:
                continue
            if vod.broadcast_date.date() > e.end_date:
                continue
            if e.channel_query_string is not None and e.channel_query_string not in vod.title:
                continue
            event = e
            break

        if event is None:
            return Response('Could not find an event for the vod',
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            team_one = event.teams.get(name=request.data['team_one'])
        except models.Team.DoesNotExist:
            return Response('Team "{}" is not participating in {}'.format(request.data['team_one'], event.name),
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            team_two = event.teams.get(name=request.data['team_two'])
        except models.Team.DoesNotExist:
            return Response('Team "{}" is not participating in {}'.format(request.data['team_two'], event.name),
                            status=status.HTTP_400_BAD_REQUEST)
        print(vod, event, team_one, team_two)
        matches = models.Match.objects.filter(teams__id__in=[team_one.id, team_two.id], event=event)
        match = None
        for m in matches:
            if len(m.teams.filter(id__in=[team_one.id, team_two.id])) == 2:
                match = m
                break
        print(match)
        if match is None:
            match = models.Match.objects.create(event=event)
            match.teams.add(team_one)
            match.teams.add(team_two)
        print(match)
        game_number = 1
        if 'game_number' in request.data:
            game_number = int(request.data['game_number'])
        try:
            game = models.Game.objects.get(game_number=game_number, match=match)
        except models.Game.DoesNotExist:
            left_participation = models.TeamParticipation.objects.create(team=team_one)
            for i, p in enumerate(team_one.players.all()):
                pp = models.PlayerParticipation.objects.create(player=p,
                                                               team_participation=left_participation, player_index=i)
                if i == 5:
                    break
            right_participation = models.TeamParticipation.objects.create(team=team_two)
            for i, p in enumerate(team_two.players.all()):
                pp = models.PlayerParticipation.objects.create(player=p,
                                                               team_participation=right_participation, player_index=i)
                if i == 5:
                    break
            game = models.Game.objects.create(game_number=game_number, match=match, left_team=left_participation,
                                              right_team=right_participation, map = models.Map.objects.first())
        for i, r_data in enumerate(request.data['rounds']):
            print(r_data)
            try:
                print(Decimal(r_data['begin']), Decimal(str(r_data['begin'])))
                print([(x.begin, x.end) for x in models.Round.objects.filter(game=game, stream_vod=vod)])
                r = models.Round.objects.get(game=game, stream_vod=vod, begin=r_data['begin'], end=r_data['end'])
                print('found it!')
            except models.Round.DoesNotExist:
                r = models.Round.objects.create(stream_vod=vod, round_number=i+1, game=game, begin=r_data['begin'], end=r_data['end'])
        return Response({'success':True})

    @action(methods=['get'], detail=False)
    def round_events(self, request):
        vods = models.StreamVod.objects.filter(status='T').all()
        print(vods)
        return Response(serializers.VodAnnotateSerializer(vods, many=True).data)


class TrainPlayerViewSet(viewsets.ModelViewSet):
    model = models.Player
    serializer_class = serializers.PlayerSerializer

    def get_queryset(self):
        rounds = models.Round.objects.filter(annotation_status='M').order_by('pk').prefetch_related(
            'game__left_team__playerparticipation_set', 'game__right_team__playerparticipation_set').all()
        players = []
        for r in rounds:
            for p in r.game.left_team.playerparticipation_set.all():
                if p.player not in players:
                    players.append(p.player)
            for p in r.game.right_team.playerparticipation_set.all():
                if p.player not in players:
                    players.append(p.player)

        return players


class AnnotateRoundViewSet(viewsets.ModelViewSet):
    model = models.Round
    #queryset = models.Round.objects.filter(annotation_status__in=['O']).filter(
    #    game__match__event__name='overwatch league - season 1').order_by('game__match__film_format', 'pk').all()
    queryset = models.Round.objects.filter(annotation_status__in=['O', 'N']).all()
    serializer_class = serializers.RoundDisplaySerializer

    def create(self, request, *args, **kwargs):
        print(request.data)
        return Response()

    def update(self, request, *args, **kwargs):
        errors = []
        error_log_path = r'E:\Data\Overwatch\issues.txt'
        instance = self.get_object()
        left = [x.player for x in instance.game.left_team.playerparticipation_set.all()]
        left_color = instance.game.left_team.get_color_display().lower()
        print(left)
        right = [x.player for x in instance.game.right_team.playerparticipation_set.all()]
        print(right)
        if not request.data.get('ignore_switches', False):
            instance.switch_set.all().delete()
        instance.ultgain_set.all().delete()
        instance.ultuse_set.all().delete()
        instance.ultend_set.all().delete()
        instance.replay_set.all().delete()
        instance.statuseffect_set.all().delete()
        switches = []
        ult_gains = []
        ult_uses = []
        ult_ends = []
        status_models = {}
        status_effects = []

        for s in ['antiheal', 'asleep', 'frozen', 'hacked', 'stunned']:
            status_models[s] = models.Status.objects.get(name__iexact=s)
        replays = []
        for r in request.data['replays']:
            replays.append(models.Replay(round=instance, start_time=r['begin'], end_time=r['end']))
        models.Replay.objects.bulk_create(replays)
        sequences = instance.sequences
        for k, v in request.data['player'].items():
            side, num = k.split('_')
            num = int(num)
            if side == 'left':
                p = left[num]
            else:
                p = right[num]
            if not request.data.get('ignore_switches', False):
                for s in v['switches']:
                    for seq in sequences:
                        if seq[0] <= s[0] <= seq[1]:
                            break
                    else:
                        continue
                    hero = models.Hero.objects.get(name__iexact=s[1])
                    switches.append(models.Switch(round=instance, player=p, new_hero=hero, time_point=s[0]))
            for s in ['antiheal', 'asleep', 'frozen', 'hacked', 'stunned']:
                m = status_models[s]
                for st in v[s]:
                    status_effects.append(models.StatusEffect(player=p,round=instance, start_time=st['begin'], end_time=st['end'], status=m))
            for ug in v['ult_gains']:
                for seq in sequences:
                    if seq[0] <= ug <= seq[1]:
                        break
                else:
                    continue
                ult_gains.append(models.UltGain(player=p, round=instance, time_point=ug))
            for uu in v['ult_uses']:
                for seq in sequences:
                    if seq[0] <= uu <= seq[1]:
                        break
                else:
                    continue
                ult_uses.append(models.UltUse(player=p, round=instance, time_point=uu))
            for ue in v['ult_ends']:
                for seq in sequences:
                    if seq[0] <= ue <= seq[1]:
                        break
                else:
                    continue
                ult_ends.append(models.UltUse(player=p, round=instance, time_point=ue))
        if not request.data.get('ignore_switches', False):
            models.Switch.objects.bulk_create(switches)
        models.UltGain.objects.bulk_create(ult_gains)
        models.UltUse.objects.bulk_create(ult_uses)
        models.UltEnd.objects.bulk_create(ult_ends)
        models.StatusEffect.objects.bulk_create(status_effects)

        instance.kill_set.all().delete()
        instance.killnpc_set.all().delete()
        instance.death_set.all().delete()
        instance.npcdeath_set.all().delete()
        instance.revive_set.all().delete()

        revives = []
        deaths = []
        npcdeaths = []
        kills = []
        killnpcs = []
        for event in request.data['kill_feed']:
            print(event)
            time_point = round(event['time_point'], 1)
            for seq in sequences:
                if seq[0] <= time_point <= seq[1]:
                    break
            else:
                continue

            event = event['event']
            if event['ability'] == 'resurrect':
                if event['first_color'] == left_color:
                    side = 'left'
                else:
                    side = 'right'
                reviving_player = instance.get_player_of_hero(event['first_hero'], time_point, side)
                revived_player = instance.get_player_of_hero(event['second_hero'], time_point, side)
                print('reviving_player', reviving_player)
                print('revived_player', revived_player)
                if reviving_player is None:
                    errors.append((instance.id, time_point, 'revive', event['first_hero'], side))
                    continue
                if revived_player is None:
                    errors.append((instance.id, time_point, 'revive', event['second_hero'], side))
                    continue
                ability = models.Ability.objects.get(name='Resurrect')
                revives.append(
                    models.Revive(reviving_player=reviving_player, revived_player=revived_player, round=instance,
                                  time_point=time_point, ability=ability))
            elif event['first_hero'] == 'n/a':
                # death
                if event['second_color'] == left_color:
                    side = 'left'
                else:
                    side = 'right'
                try:
                    npc = models.NPC.objects.get(name__iexact=event['second_hero'])
                    npcdeaths.append(
                        models.NPCDeath(round=instance, time_point=time_point, npc=npc, side=side[0].upper()))
                except models.NPC.DoesNotExist:
                    # Hero death
                    dying_player = instance.get_player_of_hero(event['second_hero'], time_point, side)
                    print('dying player', dying_player)
                    if dying_player is None:
                        errors.append((instance.id, time_point, 'death', event['second_hero'], side))
                        continue
                    deaths.append(models.Death(round=instance, time_point=time_point, player=dying_player))
            else:
                # kills
                if event['second_color'] == left_color:
                    killing_side = 'right'
                    killed_side = 'left'
                else:
                    killing_side = 'left'
                    killed_side = 'right'
                killing_player = instance.get_player_of_hero(event['first_hero'], time_point, killing_side)
                print('killing_player', killing_player)
                if killing_player is None:
                    errors.append((instance.id, time_point, 'kill', event['first_hero'], killing_side))
                    continue
                hero = models.Hero.objects.get(name__iexact=event['first_hero'])
                headshot = event['headshot']
                ability = event['ability'].replace(' headshot', '')
                ability = hero.abilities.filter(name__iexact=ability).first()
                assists = []
                for a in event['assists']:
                    hero = models.Hero.objects.get(name__iexact=a.replace('_assist', ''))
                    assists.append(hero.name)
                print(assists)
                try:
                    npc = models.NPC.objects.get(name__iexact=event['second_hero'])
                    if ability is not None:
                        if not assists:
                            killnpcs.append(
                                models.KillNPC(round=instance, time_point=time_point, killing_player=killing_player,
                                               killed_npc=npc, ability=ability))
                            npcdeaths.append(models.NPCDeath(round=instance, time_point=time_point, npc=npc,
                                                             side=killed_side[0].upper()))
                        else:
                            m = models.KillNPC.objects.create(round=instance, time_point=time_point, killing_player=killing_player,
                                           killed_npc=npc, ability=ability)
                            for a in assists:
                                assisting_player = instance.get_player_of_hero(a, time_point, killing_side)
                                if assisting_player is None:
                                    continue
                                m.assisting_players.add(assisting_player)
                except models.NPC.DoesNotExist:
                    killed_player = instance.get_player_of_hero(event['second_hero'], time_point, killed_side)
                    print('killed_player', killed_player)
                    if killed_player is None:
                        errors.append((instance.id, time_point, 'kill', event['second_hero'], killed_side))
                        continue
                    if ability is not None:
                        if not assists:
                            kills.append(models.Kill(round=instance, time_point=time_point, killing_player=killing_player,
                                                     killed_player=killed_player, ability=ability, headshot=headshot))
                            deaths.append(models.Death(round=instance, time_point=time_point, player=killed_player))
                        else:
                            try:
                                m = models.Kill.objects.create(round=instance, time_point=time_point, killing_player=killing_player,
                                            killed_player=killed_player, ability=ability, headshot=headshot)
                                print(m)
                                for a in assists:
                                    assisting_player = instance.get_player_of_hero(a, time_point, killing_side)
                                    print('assisting_player', assisting_player)
                                    if assisting_player is None:
                                        continue
                                    m.assisting_players.add(assisting_player)
                            except django.db.utils.IntegrityError:
                                pass
        models.Revive.objects.bulk_create(revives)
        models.Death.objects.bulk_create(deaths)
        models.NPCDeath.objects.bulk_create(npcdeaths)
        models.KillNPC.objects.bulk_create(killnpcs)
        models.Kill.objects.bulk_create(kills)
        with open(error_log_path, 'a') as f:
            for e in errors:
                f.write('{}\n'.format('\t'.join(map(str, e))))
        instance.annotation_status = 'O'
        instance.save()
        return Response({'success':True})


class VodViewSet(viewsets.ModelViewSet):
    model = models.StreamVod
    queryset = models.StreamVod.objects.all()
    serializer_class = serializers.StreamVodSerializer

    def create(self, request, *args, **kwargs):
        from datetime import datetime
        print(request.data)
        try:
            b = datetime.strptime(request.data['broadcast_date'], '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            b = datetime.strptime(request.data['broadcast_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
        t = datetime.today()
        vod = models.StreamVod.objects.create(channel_id=request.data['channel'], url=request.data['url'],
                                              title=request.data['title'], status='N',
                                              broadcast_date=b, last_modified=t)
        return Response(self.serializer_class(vod).data)

    @action(methods=['get'], detail=True)
    def possible_matches(self, request, pk=None):
        vod = self.get_object()
        events = vod.channel.events.prefetch_related('match_set').all()
        matches = []
        for e in events:
            matches.extend(e.match_set.all())
        return Response(serializers.MatchSerializer(matches, many=True).data)

    @action(methods=['get'], detail=True)
    def events(self, request, pk=None):
        vod = self.get_object()
        events = vod.channel.events.all()
        return Response(serializers.EventSerializer(events, many=True).data)

    @action(methods=['get'], detail=True)
    def rounds(self, request, pk=None):
        vod = self.get_object()
        rounds = vod.round_set.all()
        return Response(serializers.RoundEditSerializer(rounds, many=True).data)

    @action(methods=['get'], detail=True)
    def games(self, request, pk=None):
        vod = self.get_object()
        games = []
        for r in vod.round_set.all():
            for g in r.game.match.game_set.all():
                if g not in games:
                    games.append(g)
        return Response(serializers.GameEditSerializer(games, many=True).data)

    @action(methods=['get'], detail=True)
    def matches(self, request, pk=None):
        vod = self.get_object()
        matches = []
        for r in vod.round_set.all():
            if r.game.match not in matches:
                matches.append(r.game.match)
        return Response(serializers.MatchEditSerializer(matches, many=True).data)


class RoundViewSet(viewsets.ModelViewSet):
    model = models.Round
    queryset = models.Round.objects.all()
    serializer_class = serializers.RoundDisplaySerializer

    def create(self, request, *args, **kwargs):
        print(request.data)
        round = models.Round.objects.create(stream_vod_id=int(request.data['vod']),
                                            round_number=request.data['round_number'],
                                            game_id=request.data['game'],
                                            attacking_side=request.data['attacking_side'],
                                            begin=request.data['begin'],
                                            end=request.data['end'])
        return Response(self.serializer_class(round).data)

    def update(self, request, *args, **kwargs):
        print(request.data)
        from django.db.models import F
        instance = self.get_object()
        if request.data['stream_vod']:
            vod = models.StreamVod.objects.get(id=request.data['stream_vod']['id'])
            instance.stream_vod = vod
        else:
            instance.vod = None
        min_shift = Decimal('0.1')
        begin_shift = Decimal(request.data['begin']).quantize(min_shift) - instance.begin
        if abs(begin_shift) >= min_shift:
            instance.switch_set.filter(time_point__gt=0).update(time_point=F('time_point') - begin_shift, end_time_point=F('end_time_point') - begin_shift)
            instance.switch_set.filter(time_point__lt=0).update(time_point=0)
            instance.kill_set.update(time_point=F('time_point') - begin_shift)
            instance.killnpc_set.update(time_point=F('time_point') - begin_shift)
            instance.death_set.update(time_point=F('time_point') - begin_shift)
            instance.npcdeath_set.update(time_point=F('time_point') - begin_shift)
            instance.revive_set.update(time_point=F('time_point') - begin_shift)
            instance.ultuse_set.update(time_point=F('time_point') - begin_shift)
            instance.ultgain_set.update(time_point=F('time_point') - begin_shift)
            instance.pointgain_set.update(time_point=F('time_point') - begin_shift)
            instance.pointflip_set.update(time_point=F('time_point') - begin_shift)
            instance.pause_set.update(start_time=F('start_time') - begin_shift, end_time=F('end_time') - begin_shift)
            instance.replay_set.update(start_time=F('start_time') - begin_shift, end_time=F('end_time') - begin_shift)
            instance.smallerwindow_set.update(start_time=F('start_time') - begin_shift, end_time=F('end_time') - begin_shift)
            instance.overtime_set.update(start_time=F('start_time') - begin_shift, end_time=F('end_time') - begin_shift)
        instance.begin = request.data['begin']
        instance.end = request.data['end']
        if request.data['annotation_status']:
            instance.annotation_status = request.data['annotation_status']
        game = request.data['game']
        if isinstance(game, dict):
            game = game['id']
        if instance.game.id != game:
            instance.game = models.Game.objects.get(id=game)
        if request.data['attacking_side']:
            instance.attacking_side = request.data['attacking_side']
        if request.data['round_number']:
            instance.round_number = int(request.data['round_number'])
        instance.save()
        return Response(self.serializer_class(instance).data)

    @action(methods=['post'], detail=True)
    def download(self, request, pk=None):
        round = self.get_object()
        round.download_video()
        return Response({'success': True})

    @action(methods=['post'], detail=True)
    def export(self, request, pk=None):
        round = self.get_object()
        round.extract_video_segments()
        return Response({'success': True})

    @action(methods=['get'], detail=True)
    def players(self, request, pk=None):
        round = self.get_object()
        game = round.game
        data = {}
        data['left_team'] = [{'id': x.player.id, 'name': x.player.name} for x in
                             game.left_team.playerparticipation_set.all()]
        data['right_team'] = [{'id': x.player.id, 'name': x.player.name} for x in
                              game.right_team.playerparticipation_set.all()]
        return Response(data)

    @action(methods=['get'], detail=True)
    def round_states(self, request, pk=None):
        r = self.get_object()
        data = {}
        data['overtimes'] = r.get_overtime_states()
        data['pauses'] = r.get_pause_states()
        data['replays'] = r.get_replay_states()
        data['point_status'] = r.get_point_status_states()
        return Response(data)

    @action(methods=['get'], detail=True)
    def kill_feed_events(self, request, pk=None):
        r = self.get_object()
        return Response(r.get_kill_feed_events())

    @action(methods=['get'], detail=True)
    def player_states(self, request, pk=None):
        r = self.get_object()
        data = r.get_player_states()
        for side, players in data.items():
            for p in players:
                for i in range(len(data[side][p]['hero'])):
                    data[side][p]['hero'][i]['hero'] = serializers.HeroSerializer(data[side][p]['hero'][i]['hero']).data

        return Response(data)

    @action(methods=['get'], detail=True)
    def hero_at_time(self, request, pk=None):
        round_object = self.get_object()
        player_id = request.query_params.get('player_id')
        player = models.Player.objects.get(pk=player_id)
        time_point = round(float(request.query_params.get('time_point', 0)), 1)
        return Response(serializers.HeroSerializer(player.get_hero_at_timepoint(round_object, time_point)).data)

    @action(methods=['get'], detail=True)
    def killfeed_at_time(self, request, pk=None):
        window = 7.3
        time_point = round(float(request.query_params.get('time_point', 0)), 1)
        round_object = self.get_object()
        events = []

        kills = round_object.kill_set.filter(time_point__gte=time_point - window, time_point__lte=time_point).all()
        expected_deaths = [(x.time_point, x.killed_player) for x in kills]
        events.extend(serializers.KillKillFeedSerializer(kills, many=True).data)

        npckills = round_object.killnpc_set.filter(time_point__gte=time_point - window,
                                                   time_point__lte=time_point).all()
        expected_npcdeaths = [(x.time_point, x.killed_npc) for x in npckills]
        events.extend(serializers.KillNPCKillFeedSerializer(npckills, many=True).data)

        deaths = round_object.death_set.filter(time_point__gte=time_point - window, time_point__lte=time_point).all()
        deaths = [x for x in deaths if (x.time_point, x.player) not in expected_deaths]
        events.extend(serializers.DeathKillFeedSerializer(deaths, many=True).data)

        npcdeaths = round_object.npcdeath_set.filter(time_point__gte=time_point - window,
                                                     time_point__lte=time_point).all()
        npcdeaths = [x for x in npcdeaths if (x.time_point, x.npc) not in expected_npcdeaths]
        events.extend(serializers.NPCDeathKillFeedSerializer(npcdeaths, many=True).data)

        revives = round_object.revive_set.filter(time_point__gte=time_point - window, time_point__lte=time_point).all()
        events.extend(serializers.ReviveKillFeedSerializer(revives, many=True).data)

        events = sorted(events, key=lambda x: -1 * x['time_point'])[:6]

        return Response(events)

    @action(methods=['get'], detail=True)
    def switches(self, request, pk=None):
        round = self.get_object()
        switches = round.switch_set.all()
        serializer = serializers.SwitchDisplaySerializer(switches, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def all_deaths(self, request, pk=None):
        round = self.get_object()
        deaths = round.death_set.all()
        serializer = serializers.DeathDisplaySerializer(deaths, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def deaths(self, request, pk=None):
        round = self.get_object()
        deaths = round.get_nonkill_deaths()
        serializer = serializers.DeathDisplaySerializer(deaths, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def all_npc_deaths(self, request, pk=None):
        round = self.get_object()
        npcdeaths = round.npcdeath_set.all()
        serializer = serializers.NPCDeathDisplaySerializer(npcdeaths, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def npc_deaths(self, request, pk=None):
        round = self.get_object()
        npcdeaths = round.get_nonkill_npcdeaths()
        serializer = serializers.NPCDeathDisplaySerializer(npcdeaths, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def ult_uses(self, request, pk=None):
        round = self.get_object()
        ultuses = round.ultuse_set.all()
        serializer = serializers.UltUseDisplaySerializer(ultuses, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def ult_gains(self, request, pk=None):
        round = self.get_object()
        ultgains = round.ultgain_set.all()
        serializer = serializers.UltGainDisplaySerializer(ultgains, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def ult_ends(self, request, pk=None):
        round = self.get_object()
        ult_ends = round.ultend_set.all()
        serializer = serializers.UltEndDisplaySerializer(ult_ends, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def ult_denials(self, request, pk=None):
        round = self.get_object()
        ult_denials = round.ultdenial_set.all()
        serializer = serializers.UltDenialEditSerializer(ult_denials, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def status_effects(self, request, pk=None):
        round = self.get_object()
        status_effects = round.statuseffect_set.all()
        serializer = serializers.StatusEffectDisplaySerializer(status_effects, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def revives(self, request, pk=None):
        round = self.get_object()
        revives = round.revive_set.all()
        serializer = serializers.ReviveDisplaySerializer(revives, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def point_gains(self, request, pk=None):
        round = self.get_object()
        pointgains = round.pointgain_set.all()
        serializer = serializers.PointGainSerializer(pointgains, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def point_flips(self, request, pk=None):
        round = self.get_object()
        pointflips = round.pointflip_set.all()
        serializer = serializers.PointFlipSerializer(pointflips, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def pauses(self, request, pk=None):
        round = self.get_object()
        pauses = round.pause_set.all()
        serializer = serializers.PauseSerializer(pauses, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def kills(self, request, pk=None):
        round = self.get_object()
        kills = round.kill_set.all()
        serializer = serializers.KillEditSerializer(kills, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def kill_npcs(self, request, pk=None):
        round = self.get_object()
        killnpcs = round.killnpc_set.all()
        serializer = serializers.KillNPCEditSerializer(killnpcs, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def overtimes(self, request, pk=None):
        round = self.get_object()
        overtimes = round.overtime_set.all()
        serializer = serializers.OvertimeSerializer(overtimes, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def replays(self, request, pk=None):
        round = self.get_object()
        replaystarts = round.replay_set.all()
        serializer = serializers.ReplaySerializer(replaystarts, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def smaller_windows(self, request, pk=None):
        round = self.get_object()
        smaller_windows = round.smallerwindow_set.all()
        serializer = serializers.SmallerWindowSerializer(smaller_windows, many=True)
        return Response(serializer.data)


class SwitchViewSet(viewsets.ModelViewSet):
    model = models.Switch
    queryset = models.Switch.objects.all()
    serializer_class = serializers.SwitchSerializer

    def create(self, request, *args, **kwargs):
        instance = models.Switch.objects.create(time_point=round(request.data['time_point'], 1), player_id=request.data['player'], round_id=request.data['round'], new_hero_id=request.data['new_hero'])
        instance.round.fix_switch_end_points()
        return Response(self.serializer_class(instance).data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.time_point = request.data['time_point']
        instance.save()
        instance.round.fix_switch_end_points()
        return Response(self.serializer_class(instance).data)


class DeathViewSet(viewsets.ModelViewSet):
    model = models.Death
    queryset = models.Death.objects.all()
    serializer_class = serializers.DeathSerializer

    def create(self, request, *args, **kwargs):
        request.data['time_point'] = round(request.data['time_point'], 1)
        return super(DeathViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.time_point = request.data['time_point']
        instance.save()
        return Response()


class NPCDeathViewSet(viewsets.ModelViewSet):
    model = models.NPCDeath
    queryset = models.NPCDeath.objects.all()
    serializer_class = serializers.NPCDeathSerializer

    def create(self, request, *args, **kwargs):
        request.data['time_point'] = round(request.data['time_point'], 1)
        return super(NPCDeathViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.time_point = request.data['time_point']
        instance.side = request.data['side']
        instance.save()
        return Response()


class PauseViewSet(viewsets.ModelViewSet):
    model = models.Pause
    queryset = models.Pause.objects.all()
    serializer_class = serializers.PauseSerializer

    def create(self, request, *args, **kwargs):
        request.data['start_time'] = round(request.data['start_time'], 1)
        end_time = request.data.get('end_time', None)
        if end_time is not None:
            request.data['end_time'] = round(end_time, 1)
        return super(PauseViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.start_time = request.data['start_time']
        instance.end_time = request.data['end_time']
        instance.save()
        return Response()


class ReplayViewSet(viewsets.ModelViewSet):
    model = models.Replay
    queryset = models.Replay.objects.all()
    serializer_class = serializers.ReplaySerializer

    def create(self, request, *args, **kwargs):
        request.data['start_time'] = round(request.data['start_time'], 1)
        end_time = request.data.get('end_time', None)
        if end_time is not None:
            request.data['end_time'] = round(end_time, 1)
        return super(ReplayViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.start_time = request.data['start_time']
        instance.end_time = request.data['end_time']
        instance.save()
        return Response()


class OvertimeViewSet(viewsets.ModelViewSet):
    model = models.Overtime
    queryset = models.Overtime.objects.all()
    serializer_class = serializers.OvertimeSerializer

    def create(self, request, *args, **kwargs):
        request.data['start_time'] = round(request.data['start_time'], 1)
        end_time = request.data.get('end_time', None)
        if end_time is not None:
            request.data['end_time'] = round(end_time, 1)
        return super(OvertimeViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.start_time = request.data['start_time']
        instance.end_time = request.data['end_time']
        instance.save()
        return Response()


class SmallerWindowViewSet(viewsets.ModelViewSet):
    model = models.SmallerWindow
    queryset = models.SmallerWindow.objects.all()
    serializer_class = serializers.SmallerWindowSerializer

    def create(self, request, *args, **kwargs):
        request.data['start_time'] = round(request.data['start_time'], 1)
        end_time = request.data.get('end_time', None)
        if end_time is not None:
            request.data['end_time'] = round(end_time, 1)
        return super(SmallerWindowViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.start_time = request.data['start_time']
        instance.end_time = request.data['end_time']
        instance.save()
        return Response()


class KillViewSet(viewsets.ModelViewSet):
    model = models.Kill
    queryset = models.Kill.objects.all()
    serializer_class = serializers.KillSerializer

    def create(self, request, *args, **kwargs):
        request.data['time_point'] = round(request.data['time_point'], 1)
        m = models.Kill(round_id=request.data['round'], time_point=request.data['time_point'],
                        killing_player_id=request.data['killing_player'],
                        killed_player_id=request.data['killed_player'],
                        ability_id=request.data['ability'], headshot=request.data.get('headshot', False))
        m.save()
        return Response(self.serializer_class(m).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        death = instance.get_corresponding_death()
        death.delete()
        instance.delete()
        return Response()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.assisting_players.clear()
        for p in request.data['assisting_players']:
            instance.assisting_players.add(models.Player.objects.get(pk=p))

        corresponding_death = instance.get_corresponding_death()
        corresponding_death.time_point = request.data['time_point']
        corresponding_death.save()
        instance.time_point = round(request.data['time_point'], 1)
        instance.ability_id = request.data['ability']['id']
        instance.headshot = request.data['headshot']
        instance.save()
        return Response()


class ReviveViewSet(viewsets.ModelViewSet):
    model = models.Revive
    queryset = models.Revive.objects.all()
    serializer_class = serializers.ReviveSerializer

    def create(self, request, *args, **kwargs):
        request.data['time_point'] = round(request.data['time_point'], 1)
        return super(ReviveViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.time_point = request.data['time_point']
        instance.save()
        return Response()


class UltGainViewSet(viewsets.ModelViewSet):
    model = models.UltGain
    queryset = models.UltGain.objects.all()
    serializer_class = serializers.UltGainSerializer

    def create(self, request, *args, **kwargs):
        request.data['time_point'] = round(request.data['time_point'], 1)
        return super(UltGainViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.time_point = request.data['time_point']
        instance.save()
        return Response()


class UltEndViewSet(viewsets.ModelViewSet):
    model = models.UltEnd
    queryset = models.UltEnd.objects.all()
    serializer_class = serializers.UltEndSerializer

    def create(self, request, *args, **kwargs):
        request.data['time_point'] = round(request.data['time_point'], 1)
        return super(UltEndViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.time_point = request.data['time_point']
        instance.save()
        return Response()


class UltDenialViewSet(viewsets.ModelViewSet):
    model = models.UltDenial
    queryset = models.UltDenial.objects.all()
    serializer_class = serializers.UltDenialSerializer

    def create(self, request, *args, **kwargs):
        print(request.data)
        request.data['time_point'] = round(request.data['time_point'], 1)
        return super(UltDenialViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.time_point = request.data['time_point']
        instance.save()
        return Response()


class StatusEffectViewSet(viewsets.ModelViewSet):
    model = models.StatusEffect
    queryset = models.StatusEffect.objects.all()
    serializer_class = serializers.StatusEffectSerializer

    def create(self, request, *args, **kwargs):
        request.data['start_time'] = round(request.data['start_time'], 1)
        request.data['end_time'] = round(request.data['end_time'], 1)
        print(request.data)
        return super(StatusEffectViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.start_time = round(request.data['start_time'], 1)
        instance.end_time = round(request.data['end_time'], 1)
        instance.save()
        return Response()


class UltUseViewSet(viewsets.ModelViewSet):
    model = models.UltUse
    queryset = models.UltUse.objects.all()
    serializer_class = serializers.UltUseSerializer

    def create(self, request, *args, **kwargs):
        request.data['time_point'] = round(request.data['time_point'], 1)
        return super(UltUseViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.time_point = request.data['time_point']
        instance.save()
        return Response()


class PointGainViewSet(viewsets.ModelViewSet):
    model = models.PointGain
    queryset = models.PointGain.objects.all()
    serializer_class = serializers.PointGainSerializer

    def create(self, request, *args, **kwargs):
        request.data['time_point'] = round(request.data['time_point'], 1)

        return super(PointGainViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.time_point = request.data['time_point']
        instance.save()
        return Response()


class PointFlipViewSet(viewsets.ModelViewSet):
    model = models.PointFlip
    queryset = models.PointFlip.objects.all()
    serializer_class = serializers.PointFlipSerializer

    def create(self, request, *args, **kwargs):
        request.data['time_point'] = round(request.data['time_point'], 1)
        return super(PointFlipViewSet
                     , self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        print(request)
        instance = self.get_object()
        instance.time_point = request.data['time_point']
        instance.controlling_side = request.data['controlling_side']
        instance.save()
        return Response()


class KillNPCViewSet(viewsets.ModelViewSet):
    model = models.KillNPC
    queryset = models.KillNPC.objects.all()
    serializer_class = serializers.KillNPCSerializer

    def create(self, request, *args, **kwargs):
        request.data['time_point'] = round(request.data['time_point'], 1)
        m = models.KillNPC(round_id=request.data['round'], time_point=request.data['time_point'],
                           killing_player_id=request.data['killing_player'], killed_npc_id=request.data['killed_npc'],
                           ability_id=request.data['ability'])
        m.save()
        return Response(self.serializer_class(m).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        death = instance.get_corresponding_death()
        death.delete()
        instance.delete()
        return Response()

    def update(self, request, *args, **kwargs):
        print(request)
        instance = self.get_object()
        instance.assisting_players.clear()
        for p in request.data['assisting_players']:
            instance.assisting_players.add(models.Player.objects.get(pk=p))
        corresponding_death = instance.get_corresponding_death()

        corresponding_death.time_point = request.data['time_point']
        corresponding_death.save()
        instance.time_point = request.data['time_point']
        instance.save()
        return Response()



