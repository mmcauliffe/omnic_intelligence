from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from django.db.models import F

from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as csv_r
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import filters

from rest_framework import pagination, status

import jamotools
import django
from django.http import HttpResponse
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
        # print(dir(request))
        # print(request.auth)
        # print(request.data)
        # print(request.user)
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


class TrainStatsViewSet(viewsets.ModelViewSet):
    queryset = models.Round.objects.filter(annotation_status='M').all()
    renderer_classes = (csv_r.CSVRenderer, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    serializer_class = serializers.RoundAnalysisSerializer

    def list(self, request, *args, **kwargs):
        import csv
        response = HttpResponse(content_type='text/csv')
        response.encoding = 'utf8'
        response['Content-Disposition'] = 'attachment; filename="train_stats.csv"'
        queryset = self.get_queryset()
        data = []
        heroes = models.Hero.objects.all()
        statuses = models.Status.objects.all()
        header = list(self.serializer_class.Meta.fields)
        header += [x.name for x in heroes]
        header += [x.name for x in statuses]
        for r in queryset:
            base_data = self.serializer_class(r).data
            hero_play_time = {x.name: 0 for x in heroes}
            hero_play_time.update(r.get_hero_play_time())
            base_data.update(hero_play_time)
            status_durations = {x.name: 0 for x in statuses}
            status_durations.update(r.get_status_duration())
            base_data.update(status_durations)
            data.append(base_data)
        writer = csv.DictWriter(response, fieldnames=header)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return response


class TrainInfoViewSet(viewsets.ViewSet):
    @action(methods=['get'], detail=False)
    def stats(self, request):
        from collections import Counter
        data = {}
        for r in models.Round.objects.prefetch_related('game__match__event',
                                                       'game__map', 'stream_vod').filter(annotation_status='M').all():
            spec_mode = r.game.match.event.get_spectator_mode_display()
            if spec_mode not in data:
                data[spec_mode] = {'hero_play_time': Counter(),
                                     'ability_use': Counter(), 'map_time': Counter(),
                'npc_deaths': Counter(), 'ult_eats': Counter(),
                'spectator_mode_time': Counter(), 'film_format_time': Counter(), 'total_time': 0}
            data[spec_mode]['total_time'] += r.duration
            data[spec_mode]['hero_play_time'].update(r.get_hero_play_time())
            kill_feed_events = r.killfeedevent_set.prefetch_related('ability').all()
            for kfe in kill_feed_events:
                if kfe.ability is not None:
                    data[spec_mode]['ability_use'][kfe.ability.name] += 1
                    if kfe.ability.type == models.Ability.DAMAGING_TYPE and kfe.dying_npc is not None:
                        data[spec_mode]['npc_deaths'][kfe.dying_npc.name] += 1
                    elif kfe.ability.type == models.Ability.DENYING_TYPE and kfe.denied_ult is not None:
                        data[spec_mode]['ult_eats'][kfe.denied_ult.name] += 1
            data[spec_mode]['map_time'][r.game.map.name] += r.duration
            if r.stream_vod is not None:
                data[spec_mode]['film_format_time'][r.stream_vod.get_film_format_display()] += r.duration
        for spec_mode in data.keys():
            for k, v in data[spec_mode].items():
                if isinstance(v, dict):
                    data[spec_mode][k] = dict(sorted(v.items(), key=lambda x: -1 * x[1]))
        return Response(data)

    def list(self, request):
        max_heroes = 50
        max_labels = 250
        max_maps = 40
        max_spectator_modes = 20
        max_film_formats = 20
        max_statuses = 15
        heroes = models.Hero.objects.exclude(name__iexact='n/a').order_by('id').prefetch_related('npc_set').prefetch_related('abilities').all()
        maps = models.Map.objects.order_by('id').all()
        map_modes = [x[1].lower() for x in models.Map.MODE_CHOICES]
        submaps = []
        for m in maps:
            if m.mode == 'C':
                for s in m.submap_set.all():
                    submaps.append(s.display_name.lower())
            else:
                if m.mode == 'A':
                    max_points = 2
                else:
                    max_points = 3
                for i in range(1, max_points+1):
                    submaps.append('{}_{}'.format(m.name.lower(), i))

        colors = [x[1].lower() for x in models.TeamParticipation.COLOR_CHOICES]
        spectator_modes = [x.name.lower() for x in models.SpectatorMode.objects.all()]
        film_formats = [x.name.lower() for x in models.FilmFormat.objects.all()]
        characters = set()
        for p in models.Player.objects.all():
            name = p.name.lower()
            name = jamotools.split_syllables(name)
            characters.update(name)
        npcs = []
        labels = ['neither', 'left', 'right', 'headshot', 'environmental']
        #for c in colors + ['nonwhite']:
        #    labels.append(c)
        for h in heroes:
            labels.append(h.name.lower())
            labels.append(h.name.lower() + '_assist')
            for a in h.abilities.all():
                name = a.name.lower()
                if name not in labels:
                    labels.append(name)
            for n in h.npc_set.all():
                npcs.append(n.name.lower())
                labels.append(n.name.lower() + '_npc')
            for a in h.abilities.filter(deniable=True).all():
                labels.append(a.name.lower() + '_npc')
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
        while len(film_formats) < max_film_formats:
            film_formats.append('')
        extra_statuses = models.Status.objects.filter(independent=True).order_by('id').all()
        status_values = ['normal'] + [x.name.lower() for x in
                                      models.Status.objects.filter(independent=False).order_by('id').all()]

        extra_statuses = [x.name.lower() for x in extra_statuses]
        while len(status_values) < max_statuses:
            status_values.append('')
        game_states = ['not_game', 'game', 'pause', 'replay', 'smaller_window']
        for pt in models.PauseType.objects.all():
            if 'out' in pt.name.lower():
                continue
            elif 'game' in pt.name.lower():
                continue
            game_states.append('pause_' + pt.name.lower())
        for pt in models.ReplayType.objects.all():
            game_states.append('replay_' + pt.name.lower())
        for pt in models.SmallerWindowType.objects.all():
            game_states.append('smaller_window_' + pt.name.lower())
        data = {
            'heroes': heroes,
            'map_modes': map_modes,
            'maps': maps,
            'game': game_states,
            'submaps': submaps,
            'npcs': npcs,
            'status': status_values,
            'extra_statuses': extra_statuses,
            'colors': colors,
            'spectator_modes': spectator_modes,
            'film_formats': film_formats,
            'player_name_characters': sorted(characters),
            'kill_feed_labels': labels
        }
        for k, v in data.items():
            print(k, len(v))
        return Response(data)


class TeamColorViewSet(viewsets.ViewSet):
    def list(self, request):
        choices = [{'id': x[0], 'name': x[1]} for x in models.TeamParticipation.COLOR_CHOICES]
        return Response(choices)


class MapModeViewSet(viewsets.ViewSet):
    def list(self, request):
        choices = [x[1] for x in models.Map.MODE_CHOICES]
        return Response(choices)


class FilmFormatViewSet(viewsets.ModelViewSet):
    model = models.FilmFormat
    queryset = models.FilmFormat.objects.all()
    serializer_class = serializers.FilmFormatSerializer


class SideViewSet(viewsets.ViewSet):
    def list(self, request):
        choices = [{'id': x[0], 'name': x[1]} for x in models.SIDE_CHOICES]
        return Response(choices)


class SpectatorModeViewSet(viewsets.ModelViewSet):
    model = models.SpectatorMode
    queryset = models.SpectatorMode.objects.all()
    serializer_class = serializers.SpectatorModeSerializer


class PauseTypeViewSet(viewsets.ModelViewSet):
    model = models.PauseType
    queryset = models.PauseType.objects.all()
    serializer_class = serializers.PauseTypeSerializer


class ReplayTypeViewSet(viewsets.ModelViewSet):
    model = models.ReplayType
    queryset = models.ReplayType.objects.all()
    serializer_class = serializers.ReplayTypeSerializer


class SmallerWindowTypeViewSet(viewsets.ModelViewSet):
    model = models.SmallerWindowType
    queryset = models.SmallerWindowType.objects.all()
    serializer_class = serializers.SmallerWindowTypeSerializer


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
    queryset = models.Hero.objects.prefetch_related('abilities', 'npc_set').all()
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
        abilities = models.Ability.objects.filter(type=models.Ability.DAMAGING_TYPE).all()
        serializer = serializers.AbilitySerializer(abilities, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def reviving_abilities(self, request):
        abilities = models.Ability.objects.filter(type=models.Ability.REVIVING_TYPE).all()
        serializer = serializers.AbilitySerializer(abilities, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def denying_abilities(self, request):
        abilities = models.Ability.objects.filter(type=models.Ability.DENYING_TYPE).all()
        serializer = serializers.AbilitySerializer(abilities, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def deniable_abilities(self, request):
        abilities = models.Ability.objects.filter(deniable=True).all()
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


class SubmapViewSet(viewsets.ModelViewSet):
    model = models.Submap
    queryset = models.Submap.objects.all()
    serializer_class = serializers.SubmapSerializer


class NPCViewSet(viewsets.ModelViewSet):
    model = models.NPC
    queryset = models.NPC.objects.all()
    serializer_class = serializers.NPCSerializer


class TeamViewSet(viewsets.ModelViewSet):
    model = models.Team
    queryset = models.Team.objects.all()
    serializer_class = serializers.TeamSerializer


class TeamStatusViewSet(viewsets.ModelViewSet):
    model = models.Team
    queryset = models.Team.objects.all()
    serializer_class = serializers.TeamSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    model = models.Player
    queryset = models.Player.objects.all()
    serializer_class = serializers.PlayerSerializer


class PlayerStatusViewSet(viewsets.ModelViewSet):
    model = models.Player
    queryset = models.Player.objects.all()
    serializer_class = serializers.PlayerStatusSerializer

    filter_backends = (filters.SearchFilter, RelatedOrderingFilter,)
    pagination_class = pagination.LimitOffsetPagination
    search_fields = ('name',)

    def get_queryset(self):
        queryset = models.Player.objects.all()
        name_search = self.request.query_params.get('name', None)
        if name_search:
            queryset = queryset.filter(name__icontains=name_search)
        return queryset

    @action(methods=['get'], detail=True)
    def stats(self, request, pk=None):
        player = self.get_object()
        stats = player.generate_stats()
        stats['stats'] = [{'name': k.replace('_', ' ').title(), 'value': v} for k,v  in stats['stats'].items()]
        stats['hero_play_time'] = [{'name': k, 'value': v} for k, v in sorted(stats['hero_play_time'].items(), key=lambda x: -1 * x[1])]
        return Response(stats)

    @action(methods=['get'], detail=True)
    def teams(self, request, pk=None):
        player = self.get_object()
        q = player.affiliation_set.all()
        s = serializers.AffiliationSerializer(q, many=True)
        return Response(s.data)

    @action(methods=['get'], detail=True)
    def recent_matches(self, request, pk=None):
        player = self.get_object()
        s = serializers.MatchDisplaySerializer(player.get_latest_matches(), many=True)
        return Response(s.data)

    def list(self, request, *args, **kwargs):
        print(request.query_params)
        return super(PlayerStatusViewSet, self).list(request, *args, **kwargs)


class EventViewSet(viewsets.ModelViewSet):
    model = models.Event
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventDisplaySerializer

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
        vods = []
        for c in event.stream_channels.prefetch_related('streamvod_set').all():
            query_set = c.streamvod_set

            if event.channel_query_string is not None:
                query_set = query_set.filter(title__contains=event.channel_query_string)
            if start_date:
                query_set = query_set.filter(broadcast_date__gte=start_date)
            if end_date:
                query_set = query_set.filter(broadcast_date__lte=end_date)
            vods.extend(query_set.all())
        return Response(serializers.EventVodDisplaySerializer(vods, many=True).data)

    @action(methods=['get'], detail=True)
    def available_vods(self, request, pk=None):
        import requests
        import datetime
        event = self.get_object()
        start_date = event.start_date
        end_date = event.end_date
        vods = []
        for c in event.stream_channels.prefetch_related('streamvod_set').all():
            cursor = ''
            break_early = False
            if c.site == 'T':
                key = 'fgjp7t0f365uazgs84n7t9xhf19xt2'
                response = requests.get('https://api.twitch.tv/helix/users?login={}'.format(c.name),
                                        headers={'Client-ID': key})
                data = response.json()['data'][0]
                id = data['id']
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
                key = 'AIzaSyCXLyL759IdUXcmettlS0nPbVEmlCIIloM'
                while True:
                    vod_urls = [x.url for x in c.streamvod_set.all()]
                    if not cursor:
                        url = 'https://www.googleapis.com/youtube/v3/search?key={}&channelId={}&part=snippet,id&order=date&maxResults=50'.format(
                            key, c.youtube_channel_id)
                    else:
                        url = 'https://www.googleapis.com/youtube/v3/search?key={}&channelId={}&part=snippet,id&order=date&maxResults=50&pageToken={}'.format(
                            key, c.youtube_channel_id, cursor)
                    #if event.channel_query_string is not None:
                    #    query = '&q=allintitle:"{}"'.format(event.channel_query_string)
                    #    query = query.replace(' ', '+').replace(':', '%3A')
                    #    url += query
                    if end_date is not None:
                        mod_end_date = end_date + datetime.timedelta(days=1)  # Inclusive
                        query = '&publishedBefore=' + mod_end_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                        url += query
                    if start_date is not None:
                        mod_start_date = start_date - datetime.timedelta(days=1)  # Inclusive
                        query = '&publishedAfter=' + mod_start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                        url += query
                    print(url)
                    response = requests.get(url)
                    data = response.json()
                    print(data)
                    for item in data['items']:
                        try:
                            url = 'https://www.youtube.com/watch?v=' + item['id']['videoId']
                        except KeyError:
                            continue
                        if event.channel_query_string is not None and event.channel_query_string not in item['snippet']['title']:
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
                        cursor = data['nextPageToken']
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
    def stats(self, request, pk=None):
        all_stats = request.query_params.get('all_stats', False)
        instance = self.get_object()
        return Response(instance.generate_stats(all_stats=all_stats))

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
            return Response('Game already exists for this match.', status=status.HTTP_409_CONFLICT)
        except models.Game.DoesNotExist:
            pass

        if 'left_team' in request.data:
            print(request.data)
            left_team_participation = models.TeamParticipation.objects.create(team_id=request.data['left_team']['team'],
                                                                              color=request.data['left_team']['color'])
            pps = []
            for p in request.data['left_team']['players']:
                pps.append(models.PlayerParticipation(team_participation=left_team_participation, player_id=p['player'],
                                                               player_index=p['player_index']))

            right_team_participation = models.TeamParticipation.objects.create(team_id=request.data['right_team']['team'],
                                                                               color=request.data['right_team']['color'])
            for p in request.data['right_team']['players']:
                pps.append(models.PlayerParticipation(team_participation=right_team_participation, player_id=p['player'],
                                                               player_index=p['player_index']))
            models.PlayerParticipation.objects.bulk_create(pps)
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

    @action(methods=['get'], detail=True)
    def stats(self, request, pk=None):
        instance = self.get_object()
        return Response(instance.generate_stats())

    @action(methods=['get'], detail=True)
    def team_fight_summary(self, request, pk=None):
        instance = self.get_object()
        return Response(instance.generate_team_fight_summary())

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
        instance.game_number = request.data['game_number']
        instance.right_team.color = value
        instance.right_team.save()
        instance.save()
        return Response(self.serializer_class(instance).data)

    @action(methods=['put'], detail=True)
    def update_teams(self, request, pk=None):
        game = self.get_object()
        left_t = models.TeamParticipation.objects.prefetch_related('playerparticipation_set').get(
            id=request.data['left_team']['id'])
        player_mapping = {}
        left_t.color = request.data['left_team']['color']
        for i, p in enumerate(left_t.playerparticipation_set.all()):
            if p.player_id != request.data['left_team']['players'][i]['player']:
                player_mapping[p.player_id] = request.data['left_team']['players'][i]['player']
                p.player_id = request.data['left_team']['players'][i]['player']
                p.save()
        left_t.save()
        game.left_team = left_t
        right_t = models.TeamParticipation.objects.prefetch_related('playerparticipation_set').get(
            id=request.data['right_team']['id'])
        right_t.color = request.data['right_team']['color']
        for i, p in enumerate(right_t.playerparticipation_set.all()):
            if p.player_id != request.data['right_team']['players'][i]['player']:
                player_mapping[p.player_id] = request.data['right_team']['players'][i]['player']
                p.player_id = request.data['right_team']['players'][i]['player']
                p.save()
        right_t.save()
        game.right_team = right_t
        game.save()
        for old_p, new_p in player_mapping.items():
            models.HeroPick.objects.filter(round__game=game, player_id=old_p).update(player_id=new_p)
            models.Ultimate.objects.filter(round__game=game, player_id=old_p).update(player_id=new_p)
            models.StatusEffect.objects.filter(round__game=game, player_id=old_p).update(player_id=new_p)
            models.KillFeedEvent.objects.filter(round__game=game, killing_player_id=old_p).update(killing_player_id=new_p)
            models.KillFeedEvent.objects.filter(round__game=game, dying_player_id=old_p).update(dying_player_id=new_p)
            models.Assist.objects.filter(kill__round__game=game, player_id=old_p).update(player_id=new_p)
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


class BroadcastEventViewSet(viewsets.ModelViewSet):
    model = models.Round
    queryset = models.Round.objects.prefetch_related('game', 'game__match', 'game__match__event').filter(
        ~Q(stream_vod=None)).all()
    serializer_class = serializers.SimpleRoundStatusSerializer
    filter_backends = (filters.SearchFilter, RelatedOrderingFilter,)
    pagination_class = pagination.LimitOffsetPagination
    search_fields = ('game__match__event__name', 'game__match__teams__name', 'annotation_status')

    def get_queryset(self):
        rq = models.Round.objects.filter(stream_vod__isnull=False).all()
        event_type = self.request.query_params.get('event_type', None)
        type_id = self.request.query_params.get('type_id', None)
        if not event_type:
            return models.Round.objects.none()
        if event_type == 'pause':
            if type_id is None:
                rq = rq.filter(pause__start_time__gte=0, pause__type__isnull=True)
            else:
                rq = rq.filter(pause__type_id=type_id)
        elif event_type == 'replay':
            if type_id is None:
                rq = rq.filter(replay__start_time__gte=0, replay__type__isnull=True)
            else:
                rq = rq.filter(replay__type_id=type_id)
        elif event_type == 'smaller_window':
            if type_id is None:
                rq = rq.filter(smallerwindow__start_time__gte=0, smallerwindow__type__isnull=True)
            else:
                rq = rq.filter(smallerwindow__type_id=type_id)

        annotation_status = self.request.query_params.get('annotation_status', None)
        if annotation_status is not None:
            rq = rq.filter(annotation_status=annotation_status)
        spectator_mode = self.request.query_params.get('spectator_mode', None)
        if spectator_mode is not None:
            rq = rq.filter(game__match__event__spectator_mode=spectator_mode)
        return rq.distinct()

    def list(self, request, *args, **kwargs):
        print(request.query_params)
        return super(BroadcastEventViewSet, self).list(request, *args, **kwargs)


class GameParsingErrorViewSet(viewsets.ModelViewSet):
    model = models.Round
    queryset = models.Round.objects.prefetch_related('game', 'game__match', 'game__match__event').filter(
        ~Q(stream_vod=None)).all()
    serializer_class = serializers.RoundStatusSerializer
    filter_backends = (filters.SearchFilter, RelatedOrderingFilter,)
    pagination_class = pagination.LimitOffsetPagination
    search_fields = ('game__match__event__name', 'game__match__teams__name', 'annotation_status')

    def get_queryset(self):
        rounds = []

        rq = models.Round.objects.filter(exclude_for_training=False).prefetch_related('game').all()

        annotation_status = self.request.query_params.get('annotation_status', None)
        if annotation_status is not None:
            rq = rq.filter(annotation_status=annotation_status)
        spectator_mode = self.request.query_params.get('spectator_mode', None)
        if spectator_mode is not None:
            rq = rq.filter(game__match__event__spectator_mode=spectator_mode)
        for r in rq:
            if r.has_overlapping_heroes() or r.has_many_empty_deaths() or \
                    r.game.left_team.player_count() < 6 or r.game.right_team.player_count() < 6:
                rounds.append(r.id)
        queryset = models.Round.objects.filter(id__in=rounds).all()
        return queryset

    def list(self, request, *args, **kwargs):
        print(request.query_params)
        return super(GameParsingErrorViewSet, self).list(request, *args, **kwargs)


class PossibleDenySearchViewSet(viewsets.ModelViewSet):
    model = models.Round
    queryset = models.Round.objects.prefetch_related('game', 'game__match', 'game__match__event').filter(
        ~Q(stream_vod=None)).all()
    serializer_class = serializers.RoundStatusSerializer
    filter_backends = (filters.SearchFilter, RelatedOrderingFilter,)
    pagination_class = pagination.LimitOffsetPagination
    search_fields = ('game__match__event__name', 'game__match__teams__name', 'annotation_status')

    def get_queryset(self):
        min_ult_duration = 0.3
        max_ult_duration = 2
        rounds = []
        hero = self.request.query_params.get('hero', None)
        if hero is not None:
            heroes = models.Hero.objects.filter(id=hero, abilities__deniable=True).distinct()
        else:
            heroes = models.Hero.objects.filter(abilities__deniable=True).distinct()
        deniers = models.Hero.objects.filter(abilities__type=models.Ability.DENYING_TYPE).distinct()
        ultimates = models.Ultimate.objects.prefetch_related('round', 'player').filter(
            ended__lte=F('used') + Decimal(max_ult_duration),
            ended__gte=F('used') + Decimal(min_ult_duration))

        annotation_status = self.request.query_params.get('annotation_status', None)
        if annotation_status is not None:
            ultimates = ultimates.filter(round__annotation_status=annotation_status)
        spectator_mode = self.request.query_params.get('spectator_mode', None)
        if spectator_mode is not None:
            ultimates = ultimates.filter(round__game__match__event__spectator_mode=spectator_mode)
        for u in ultimates:
            r = u.round
            player = u.player
            h = player.get_hero_at_timepoint(r, u.gained)
            if h not in heroes:
                continue
            side = 'left'
            if player not in r.game.left_team.players.all():
                side = 'right'
            if not r.has_hero(deniers, u.ended, side):
                continue
            if r.id not in rounds:
                rounds.append(r.id)
        queryset = models.Round.objects.filter(id__in=rounds).all()
        return queryset

    def list(self, request, *args, **kwargs):
        print(request.query_params)
        return super(PossibleDenySearchViewSet, self).list(request, *args, **kwargs)


class RoundStatusViewSet(viewsets.ModelViewSet):
    model = models.Round
    queryset = models.Round.objects.prefetch_related('game', 'game__match', 'game__match__event').filter(
        ~Q(stream_vod=None)).all()
    serializer_class = serializers.RoundStatusSerializer
    filter_backends = (filters.SearchFilter, RelatedOrderingFilter,)
    pagination_class = pagination.LimitOffsetPagination
    search_fields = ('game__match__event__name', 'game__match__teams__name', 'annotation_status')

    def get_queryset(self):
        queryset = models.Round.objects.prefetch_related(
                                                         'heropick_set__new_hero').filter(
            ~Q(stream_vod=None)).all()
        annotation_status = self.request.query_params.get('annotation_status', None)
        if annotation_status is not None:
            queryset = queryset.filter(annotation_status=annotation_status)
        m = self.request.query_params.get('map', None)
        if m is not None:
            queryset = queryset.filter(game__map=m)
        spectator_mode = self.request.query_params.get('spectator_mode', None)
        if spectator_mode is not None:
            queryset = queryset.filter(game__match__event__spectator_mode=spectator_mode)
        film_format = self.request.query_params.get('film_format', None)
        if film_format is not None:
            queryset = queryset.filter(stream_vod__film_format=film_format)
        hero = self.request.query_params.get('hero', None)
        if hero is not None:
            play_time_threshold = self.request.query_params.get('play_time_threshold', None)
            if play_time_threshold:
                queryset = queryset.filter(heropick__new_hero=hero, heropick__end_time_point__gte=F('heropick__time_point') + Decimal(play_time_threshold))
            else:
                queryset = queryset.filter(heropick__new_hero=hero)
            queryset = queryset.distinct()
        ordering = self.request.query_params.get('ordering', None)
        if ordering == 'duration':
            queryset = queryset.order_by(F('end') - F('begin'))
        elif ordering == '-duration':
            queryset = queryset.order_by((F('end') - F('begin')).desc())
        return queryset

    def list(self, request, *args, **kwargs):
        print(request.query_params)
        return super(RoundStatusViewSet, self).list(request, *args, **kwargs)


class TrainRoundViewSet(viewsets.ModelViewSet):
    model = models.Round
    queryset = models.Round.objects.filter(annotation_status__in=['M', 'O'],
                                           stream_vod__id__gte=2290).exclude(exclude_for_training=True).order_by('pk').all()
    serializer_class = serializers.RoundDisplaySerializer

    def get_queryset(self):
        spectator_mode = self.request.query_params.get('spectator_mode', None)
        queryset = models.Round.get_train_set(spectator_mode)
        return queryset

    def retrieve(self, request, pk=None):
        from django.shortcuts import get_object_or_404
        queryset = models.Round.objects.all()
        round = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(round)
        return Response(serializer.data)


class ExampleRoundViewSet(viewsets.ModelViewSet):
    model = models.Round
    queryset = models.Round.objects.filter(annotation_status='M').order_by('pk').all()
    serializer_class = serializers.RoundDisplaySerializer

    def get_queryset(self):
        queryset = []
        for c in models.FILM_FORMAT_CHOICES:
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
    queryset = models.StreamVod.objects.filter(round__annotation_status__in=['O', 'M']).order_by('pk').distinct().all()
    serializer_class = serializers.VodDisplaySerializer

    def get_queryset(self):
        vods = []
        spec_modes = models.SpectatorMode.objects.all()
        for sp in spec_modes:
            round_queryset = models.Round.get_train_set(sp)
            vods.extend(models.StreamVod.objects.filter(round__in=round_queryset).distinct())
        return vods

    @action(methods=['get'], detail=False)
    def stats(self, request):
        import csv
        q = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response.encoding = 'utf8'
        response['Content-Disposition'] = 'attachment; filename="train_vod_stats.csv"'
        data = []
        header = ['id', 'film_format', 'spectator_mode']
        game_statuses = ['not_game', 'game', 'pause', 'replay', 'smaller_window']
        zooms = ['left_zoom', 'right_zoom']
        header += game_statuses + zooms
        maps = [x.name.lower() for x in models.Map.objects.all()]
        header += [x for x in maps]
        for v in q:
            d = {'id': v.id, 'film_format': v.get_film_format_display()}
            first_round = v.round_set.first()
            d['spectator_mode'] = first_round.game.match.event.get_spectator_mode_display()
            statuses = v.get_status()
            game_duration = {x: 0 for x in game_statuses}
            for m in statuses['game']:
                game_duration[m['status']] += m['end'] - m['begin']
            zoom_duration = {x: 0 for x in zooms}
            for side in ['left', 'right']:
                for m in statuses[side]:
                    if m['status'] == 'zoom':
                        zoom_duration[side+'_zoom'] += m['end'] - m['begin']
            map_duration = {x: 0 for x in maps}
            for m in statuses['map']:
                if m['status'] != 'n/a':
                    map_duration[m['status']] += m['end'] - m['begin']
            d.update(game_duration)
            d.update(zoom_duration)
            d.update(map_duration)
            data.append(d)
        writer = csv.DictWriter(response, fieldnames=header)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return response


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
    serializer_class = serializers.AnnotateVodSerializer

    @action(methods=['get'], detail=False)
    def in_out_game(self, request):
        vods = models.StreamVod.objects.filter(status='N', pk__gte=3847).all()
        return Response(self.serializer_class(vods, many=True).data)

    @action(methods=['post'], detail=False)
    def upload_in_out_game(self, request):
        print(request.data)
        vod = models.StreamVod.objects.get(id=request.data['vod_id'])
        event = vod.event

        if event is None:
            return Response('Could not find an event for the vod',
                            status=status.HTTP_400_BAD_REQUEST)
        if vod.type != 'S':
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
            matches = models.Match.objects.filter(teams__id__in=[team_one.id, team_two.id], event=event,
                                                  date=vod.broadcast_date.date())
            match = None
            for m in matches:
                if len(m.teams.filter(id__in=[team_one.id, team_two.id])) == 2:
                    match = m
                    break
            if match is None:
                match = models.Match.objects.create(event=event, date=vod.broadcast_date.date())
                match.teams.add(team_one)
                match.teams.add(team_two)
            print(match)
        if vod.type == 'G':
            game_number = 1
            num_previous_games = 0
            if 'game_number' in request.data:
                game_number = int(request.data['game_number'])
            games = [{'game_number': game_number, 'rounds': request.data['rounds'], 'map': request.data['map'],
                      'left_color': request.data['left_color'], 'right_color': request.data['right_color']}]
        elif vod.type == 'M':
            games = request.data['games']
            num_previous_games = match.game_set.count()
        else:
            num_previous_games = None
            games = []
            for m in request.data['matches']:
                for g in m['games']:
                    g['match'] = m
                    games.append(g)
        for g in games:
            if vod.type == 'S':
                try:
                    team_one = event.teams.get(name=g['match']['team_one'])
                except models.Team.DoesNotExist:
                    return Response('Team "{}" is not participating in {}'.format(g['match']['team_one'], event.name),
                                    status=status.HTTP_400_BAD_REQUEST)
                try:
                    team_two = event.teams.get(name=g['match']['team_two'])
                except models.Team.DoesNotExist:
                    return Response('Team "{}" is not participating in {}'.format(g['match']['team_two'], event.name),
                                    status=status.HTTP_400_BAD_REQUEST)

                print(vod, event, team_one, team_two)
                matches = models.Match.objects.filter(teams__id__in=[team_one.id, team_two.id], event=event,
                                                      date=vod.broadcast_date.date())
                match = None
                for m in matches:
                    if len(m.teams.filter(id__in=[team_one.id, team_two.id])) == 2:
                        match = m
                        break
                if match is None:
                    match = models.Match.objects.create(event=event, date=vod.broadcast_date.date())
                    match.teams.add(team_one)
                    match.teams.add(team_two)
                if num_previous_games is None:
                    num_previous_games = match.game_set.count()

            player_names = g['rounds'][0]['players']
            left_color = g['left_color']
            right_color = g['right_color']
            left_color_code = models.TeamParticipation.get_color_code(left_color)
            right_color_code = models.TeamParticipation.get_color_code(right_color)
            print(left_color, right_color)
            print(left_color_code, right_color_code)
            left_names = [x for x in player_names['left'].values()]
            right_names = [x for x in player_names['right'].values()]
            is_team_one_left = True
            left_players = []
            right_players = []
            for n in left_names:
                if team_one.has_player_at_date(n, match.date):
                    player = team_one.players.get(name__iexact=n)
                    left_players.append(player)
                else:
                    is_team_one_left = False
                    left_players = []
                    break
            if is_team_one_left:
                for n in right_names:
                    try:
                        player = team_two.players.get(name__iexact=n)
                        right_players.append(player)
                    except models.Player.DoesNotExist:
                        return Response('Team "{}" does not have player "{}" ()'.format(team_two.name, n,
                                                                                        [x.name for x in
                                                                                         team_two.players.all()]),
                                        status=status.HTTP_400_BAD_REQUEST)
            else:
                for n in left_names:
                    try:
                        player = team_two.players.get(name__iexact=n)
                        left_players.append(player)
                    except models.Player.DoesNotExist:
                        return Response('Team "{}" does not have player "{}" ()'.format(team_two.name, n,
                                                                                        [x.name for x in
                                                                                         team_two.players.all()]),
                                        status=status.HTTP_400_BAD_REQUEST)
                for n in right_names:
                    try:
                        player = team_one.players.get(name__iexact=n)
                        right_players.append(player)
                    except models.Player.DoesNotExist:
                        return Response('Team "{}" does not have player "{}" ()'.format(team_one.name, n,
                                                                                        [x.name for x in
                                                                                         team_one.players.all()]),
                                        status=status.HTTP_400_BAD_REQUEST)
            try:
                game = models.Game.objects.get(game_number=num_previous_games + g['game_number'], match=match)
                map = game.map
            except models.Game.DoesNotExist:
                if is_team_one_left:
                    left_participation = models.TeamParticipation.objects.create(team=team_one, color=left_color_code)
                    right_participation = models.TeamParticipation.objects.create(team=team_two, color=right_color_code)
                else:
                    left_participation = models.TeamParticipation.objects.create(team=team_two, color=left_color_code)
                    right_participation = models.TeamParticipation.objects.create(team=team_one, color=right_color_code)

                for i, p in enumerate(left_players):
                    pp = models.PlayerParticipation.objects.create(player=p,
                                                                   team_participation=left_participation,
                                                                   player_index=i)
                for i, p in enumerate(right_players):
                    pp = models.PlayerParticipation.objects.create(player=p,
                                                                   team_participation=right_participation,
                                                                   player_index=i)
                map = models.Map.objects.get(name__iexact=g['map'])
                game = models.Game.objects.create(game_number=num_previous_games + g['game_number'], match=match,
                                                  left_team=left_participation,
                                                  right_team=right_participation, map=map)
            for i, r_data in enumerate(g['rounds']):
                print(r_data)
                try:
                    print(Decimal(r_data['begin']), Decimal(str(r_data['begin'])))
                    print([(x.begin, x.end) for x in models.Round.objects.filter(game=game, stream_vod=vod)])
                    r = models.Round.objects.get(game=game, stream_vod=vod, begin=r_data['begin'], end=r_data['end'])
                    print('found it!')
                except models.Round.DoesNotExist:
                    submap = None
                    if map.mode == 'C' and 'submap' in r_data:
                        submaps = models.Submap.objects.filter(name__iexact=r_data['submap'].split('_')[-1], map=map)
                        if len(submaps) > 0:
                            submap = submaps[0]
                    r = models.Round.objects.create(stream_vod=vod, round_number=i + 1, game=game,
                                                    begin=r_data['begin'], end=r_data['end'],
                                                    attacking_side=r_data['attacking_side'], submap=submap)
                    pauses = []
                    smaller_windows = []
                    replays = []
                    zooms = []
                    for p in r_data['pauses']:
                        pt = None
                        if 'type' in p:
                            pt = models.PauseType.objects.get(name=p['type'])
                        pauses.append(models.Pause(start_time=p['begin'], end_time=p['end'], round=r, type=pt))
                    for p in r_data['replays']:
                        pt = None
                        if 'type' in p:
                            pt = models.ReplayType.objects.get(name=p['type'])
                        replays.append(models.Replay(start_time=p['begin'], end_time=p['end'], round=r, type=pt))
                    for p in r_data['smaller_windows']:
                        pt = None
                        if 'type' in p:
                            pt = models.SmallerWindowType.objects.get(name=p['type'])
                        smaller_windows.append(models.SmallerWindow(start_time=p['begin'], end_time=p['end'], round=r, type=pt))
                    for z in r_data['left_zooms']:
                        zooms.append(models.Zoom(start_time=z['begin'], end_time=z['end'], round=r, side='L'))
                    for z in r_data['right_zooms']:
                        zooms.append(models.Zoom(start_time=z['begin'], end_time=z['end'], round=r, side='R'))
                    models.Pause.objects.bulk_create(pauses)
                    models.Replay.objects.bulk_create(replays)
                    models.SmallerWindow.objects.bulk_create(smaller_windows)
                    models.Zoom.objects.bulk_create(zooms)

        vod.status = 'G'
        vod.save()
        return Response({'success': True})

    @action(methods=['get'], detail=False)
    def round_events(self, request):
        vods = models.StreamVod.objects.filter(status='T', pk__gte=3847, round_set__annotation_status='N').distinct().all()
        print(vods)
        return Response(serializers.VodAnnotateSerializer(vods, many=True).data)


class TrainPlayerViewSet(viewsets.ModelViewSet):
    model = models.Player
    serializer_class = serializers.PlayerSerializer

    def get_queryset(self):
        rounds = models.Round.objects.filter(annotation_status__in=['M', 'O']).order_by('pk').prefetch_related(
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
    # queryset = models.Round.objects.filter(annotation_status__in=['O']).filter(
    #    game__match__event__name='overwatch league - season 1').order_by('game__match__film_format', 'pk').all()
    queryset = models.Round.objects.filter(annotation_status__in=['N']).all()
    serializer_class = serializers.RoundDisplaySerializer

    def create(self, request, *args, **kwargs):
        print(request.data)
        return Response()

    def update(self, request, *args, **kwargs):
        from decimal import Decimal
        instance = self.get_object()
        left = [x.player for x in instance.game.left_team.playerparticipation_set.all()]
        print(left)
        right = [x.player for x in instance.game.right_team.playerparticipation_set.all()]
        print(right)
        if instance.game.left_team.player_count() < 6 or instance.game.right_team.player_count() < 6:
            instance.annotation_status = 'O'
            instance.save()
            return Response({'success': False, 'errors': True})
        if not request.data.get('ignore_switches', False):
            instance.heropick_set.all().delete()

        sequences = instance.sequences

        instance.teamfight_set.all().delete()
        instance.pointgain_set.all().delete()
        instance.pointflip_set.all().delete()
        instance.overtime_set.all().delete()
        point_gains = []
        point_flips = []
        overtimes = []
        for o in request.data['overtimes']:
            overtimes.append(models.Overtime(round=instance, start_time=o['begin'], end_time=o['end']))
        for p in request.data['point_flips']:
            point_flips.append(models.PointFlip(round=instance, time_point=p['time_point'],
                                                controlling_side=p['controlling_side']))
        for p in request.data['point_gains']:
            point_gains.append(
                models.PointGain(round=instance, time_point=p['time_point'], point_total=int(p['point_total'])))

        if point_gains:
            models.PointGain.objects.bulk_create(point_gains)
        if point_flips:
            models.PointFlip.objects.bulk_create(point_flips)
        if overtimes:
            models.Overtime.objects.bulk_create(overtimes)

        instance.ultimate_set.all().delete()
        instance.statuseffect_set.all().delete()
        hero_picks = []
        ultimates = []
        status_effects = []

        status_models = {x.name.lower(): x for x in models.Status.objects.all()}
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
                        if seq[0] - Decimal('0.5') <= s['begin'] <= seq[1] + Decimal('0.5'):
                            break
                    else:
                        continue
                    hero = models.Hero.objects.get(name__iexact=s['hero'])
                    hero_picks.append(models.HeroPick(round=instance, player=p, new_hero=hero,
                                                      time_point=s['begin'], end_time_point=s['end']))
            for s, m in status_models.items():
                if s not in v:
                    continue
                for st in v[s]:
                    status_effects.append(models.StatusEffect(player=p, round=instance, start_time=st['begin'],
                                                              end_time=st['end'], status=m))
            for ult in v['ultimates']:
                for seq in sequences:
                    if seq[0] - Decimal('0.5') <= ult['gained'] <= seq[1] + Decimal('0.5'):
                        break
                else:
                    continue
                m = models.Ultimate(player=p, round=instance, gained=ult['gained'])
                if 'used' in ult:
                    m.used = ult['used']
                    m.ended = ult['ended']
                ultimates.append(m)

        if not request.data.get('ignore_switches', False):
            models.HeroPick.objects.bulk_create(hero_picks)
        instance.fix_switch_end_points()
        models.Ultimate.objects.bulk_create(ultimates)
        models.StatusEffect.objects.bulk_create(status_effects)

        instance.killfeedevent_set.all().delete()

        kill_feed_events = []
        assist_objects = []
        for event in request.data['kill_feed']:
            #DEBUG
            print(event)
            time_point = round(event['time_point'], 1)
            for seq in sequences:
                if seq[0] - Decimal('0.5') <= time_point <= seq[1] + Decimal('0.5'):
                    break
            else:
                continue
            print('PROCESSING')
            event = event['event']
            if event['first_side'] == event['second_side'] and event['ability'] != 'resurrect':
                event['first_hero'] = 'n/a'
            if event['ability'] == 'resurrect':
                side = event['first_side']
                reviving_player = instance.get_player_of_hero(event['first_hero'], time_point, side)
                revived_player = instance.get_player_of_hero(event['second_hero'], time_point, side)
                if reviving_player is None:
                    print('ERROR', instance.id, time_point, 'revive', event['first_hero'], side)
                    continue
                if revived_player is None:
                    print('ERROR', instance.id, time_point, 'revive', event['second_hero'], side)
                    continue
                ability = models.Ability.objects.get(name='Resurrect')
                kill_feed_events.append(
                    models.KillFeedEvent(killing_player=reviving_player, dying_player=revived_player, round=instance,
                                         time_point=time_point, ability=ability))
            elif event['first_hero'] == 'n/a':
                # death
                side = event['second_side']
                try:
                    npc = models.NPC.objects.get(name__iexact=event['second_hero'])
                    dying_player = instance.get_player_of_hero(npc.spawning_hero.name, time_point, side)
                    kill_feed_events.append(
                        models.KillFeedEvent(round=instance, time_point=time_point, dying_player=dying_player,
                                             environmental=event.get('environmental', False),
                                             dying_npc=npc))
                except models.NPC.DoesNotExist:
                    # Hero death
                    dying_player = instance.get_player_of_hero(event['second_hero'], time_point, side)
                    if dying_player is None:
                        print('ERROR', instance.id, time_point, 'death', event['second_hero'], side)
                        continue
                    kill_feed_events.append(
                        models.KillFeedEvent(round=instance, time_point=time_point,
                                             environmental=event.get('environmental', False),
                                             dying_player=dying_player))
            else:
                # kills
                print('KILL')
                killing_side = event['first_side']
                killed_side = event['second_side']
                killing_player = instance.get_player_of_hero(event['first_hero'], time_point, killing_side)
                print(event['first_hero'], killing_player)
                if killing_player is None:
                    print('ERROR', instance.id, time_point, 'kill', event['first_hero'], killing_side)
                    continue
                hero = models.Hero.objects.get(name__iexact=event['first_hero'])
                headshot = event['headshot']
                ability_name = event['ability'].replace(' headshot', '')
                ability = hero.abilities.filter(name__iexact=ability_name).first()
                if ability is None and event['first_hero'].lower() == 'echo':
                    ability = models.Ability.objects.filter(name__iexact=ability_name).first()
                # DEBUG
                if event['first_hero'].lower() == 'echo':

                    print(event)
                    print(hero)
                    print(ability)
                assists = []
                for a in event['assisting_heroes']:
                    hero = models.Hero.objects.get(name__iexact=a.replace('_assist', ''))
                    assists.append(hero.name)
                try:
                    # NPC kill
                    npc = models.NPC.objects.get(name__iexact=event['second_hero'])
                    side = event['second_side']
                    dying_player = instance.get_player_of_hero(npc.spawning_hero.name, time_point, side)
                    if dying_player is None:
                        dying_player = instance.get_player_of_hero('Echo', time_point, side)
                        if dying_player is not None:
                            if dying_player.get_ult_state_at_timepoint(instance, time_point) != 'using_ult':
                                dying_player = None
                    if event['first_hero'].lower() == 'echo':
                        print(npc)
                        print(dying_player)
                    if ability is not None and dying_player is not None:
                        if ability.type != models.Ability.DAMAGING_TYPE:
                            ability = models.Ability.objects.get(name='Primary')
                        if not assists:
                            kill_feed_events.append(
                                models.KillFeedEvent(round=instance, time_point=time_point,
                                                     killing_player=killing_player,
                                                     dying_npc=npc, dying_player=dying_player, ability=ability,
                                                     environmental=event.get('environmental', False),
                                                     headshot=headshot))
                        else:
                            m = models.KillFeedEvent.objects.create(round=instance, time_point=time_point,
                                                                    killing_player=killing_player,
                                                                    dying_npc=npc, dying_player=dying_player,
                                                                    environmental=event.get('environmental', False),
                                                                    ability=ability, headshot=headshot)
                            for i, a in enumerate(assists):
                                assisting_player = instance.get_player_of_hero(a, time_point, killing_side)
                                if assisting_player is None:
                                    continue
                                assist_objects.append(models.Assist(player=assisting_player, kill=m, order=i))
                except models.NPC.DoesNotExist:
                    try:
                        # Ult denial
                        denied_ult = models.Ability.objects.get(name__iexact=event['second_hero'], deniable=True)
                        side = event['second_side']
                        dying_player = instance.get_player_of_hero(denied_ult.heroes.first().name, time_point, side)
                        if ability is None:
                            ability = hero.abilities.filter(type=models.Ability.DENYING_TYPE).first()
                        if dying_player is None:
                            dying_player = instance.get_player_of_hero('Echo', time_point, side)
                            if dying_player is not None:
                                if dying_player.get_ult_state_at_timepoint(instance, time_point) != 'using_ult':
                                    dying_player = None
                        if ability is not None and dying_player is not None:
                            kill_feed_events.append(
                                models.KillFeedEvent(round=instance, time_point=time_point,
                                                     killing_player=killing_player,
                                                     denied_ult=denied_ult, dying_player=dying_player, ability=ability))
                    except models.Ability.DoesNotExist:
                        # Kill
                        dying_player = instance.get_player_of_hero(event['second_hero'], time_point, killed_side)
                        if dying_player is None:
                            print('ERROR', instance.id, time_point, 'kill', event['second_hero'], killed_side)
                            continue
                        if event['first_hero'].lower() == 'echo':
                            print('kill')
                            print(dying_player)
                        if ability is not None:
                            if not assists:
                                kill_feed_events.append(models.KillFeedEvent(round=instance, time_point=time_point,
                                                                             killing_player=killing_player,
                                                                             dying_player=dying_player, ability=ability,
                                                                             environmental=event.get('environmental', False),
                                                                             headshot=headshot))
                            else:
                                try:
                                    m = models.KillFeedEvent.objects.create(round=instance, time_point=time_point,
                                                                            killing_player=killing_player,
                                                                            dying_player=dying_player, ability=ability,
                                                                            environmental=event.get('environmental', False),
                                                                            headshot=headshot)
                                    for i,a in enumerate(assists):
                                        assisting_player = instance.get_player_of_hero(a, time_point, killing_side)
                                        if assisting_player is None:
                                            continue
                                        assist_objects.append(models.Assist(player=assisting_player, kill=m, order=i))
                                except django.db.utils.IntegrityError:
                                    pass
        models.KillFeedEvent.objects.bulk_create(kill_feed_events)
        models.Assist.objects.bulk_create(assist_objects)
        instance.annotation_status = 'O'
        instance.save()
        return Response({'success': True})


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
        if 'game' in request.data['title'].lower():
            vod_type = models.StreamVod.GAME_TYPE
        else:
            vod_type = models.StreamVod.MATCH_TYPE
        original_film_format = models.FilmFormat.objects.get(code='O')
        vod = models.StreamVod.objects.create(channel_id=request.data['channel'], url=request.data['url'],
                                              title=request.data['title'], status='N',
                                              type=vod_type,
                                              film_format_id=request.data.get('film_format', original_film_format.id),
                                              broadcast_date=b, last_modified=t)
        return Response(self.serializer_class(vod).data)

    @action(methods=['get'], detail=True)
    def game_status(self, request, pk=None):
        vod = self.get_object()
        return_dict = vod.get_status()
        return Response(return_dict)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        print(request.data)
        instance.type = request.data['type']
        instance.status = request.data['status']
        instance.save()
        return Response(self.serializer_class(instance).data)

    @action(methods=['get'], detail=True)
    def possible_matches(self, request, pk=None):
        vod = self.get_object()
        events = vod.channel.events.filter(start_date__lte=vod.broadcast_date,
                                           end_date__gte=vod.broadcast_date).prefetch_related('match_set').all()
        matches = []
        for e in events:
            if e.channel_query_string is not None and e.channel_query_string not in vod.title:
                continue
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
    queryset = models.Round.objects.prefetch_related('game').all()
    serializer_class = serializers.RoundDisplaySerializer

    def create(self, request, *args, **kwargs):
        print(request.data)
        round = models.Round.objects.create(stream_vod_id=int(request.data['vod']),
                                            round_number=request.data['round_number'],
                                            game_id=request.data['game'],
                                            attacking_side=request.data['attacking_side'],
                                            submap=request.data.get('submap', None),
                                            begin=request.data['begin'],
                                            end=request.data['end'])
        return Response(self.serializer_class(round).data)

    @action(methods=['get'], detail=True)
    def team_fights(self, request, pk=None):
        r = self.get_object()
        team_fights = r.teamfight_set.all()
        serializer = serializers.TeamFightDisplaySerializer(team_fights, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def generate_team_fights(self, request, pk=None):
        r = self.get_object()
        team_fight_objects = r.generate_team_fights()
        serializer = serializers.TeamFightSerializer(team_fight_objects, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        print(request.data)
        from django.db.models import F
        instance = self.get_object()
        if request.data['stream_vod']:
            if isinstance(request.data['stream_vod'], dict):
                id = request.data['stream_vod']['id']
            else:
                id = request.data['stream_vod']
            vod = models.StreamVod.objects.get(id=id)
            instance.stream_vod = vod
        else:
            instance.vod = None
        min_shift = Decimal('0.1')
        begin_shift = Decimal(request.data['begin']).quantize(min_shift) - instance.begin
        if abs(begin_shift) >= min_shift:
            instance.heropick_set.filter(time_point__gt=0).update(time_point=F('time_point') - begin_shift,
                                                                  end_time_point=F('end_time_point') - begin_shift)
            instance.heropick_set.filter(time_point__lt=0).update(time_point=0)
            instance.killfeedevent_set.update(time_point=F('time_point') - begin_shift)
            instance.ultimate_set.update(gained=F('gained') - begin_shift)
            instance.ultimate_set.exclude(used__isnull=True).update(gained=F('used') - begin_shift)
            instance.ultimate_set.exclude(ended__isnull=True).update(gained=F('ended') - begin_shift)
            instance.pointgain_set.update(time_point=F('time_point') - begin_shift)
            instance.pointflip_set.update(time_point=F('time_point') - begin_shift)
            instance.pause_set.update(start_time=F('start_time') - begin_shift, end_time=F('end_time') - begin_shift)
            instance.replay_set.update(start_time=F('start_time') - begin_shift, end_time=F('end_time') - begin_shift)
            instance.smallerwindow_set.update(start_time=F('start_time') - begin_shift,
                                              end_time=F('end_time') - begin_shift)
            instance.zoom_set.update(start_time=F('start_time') - begin_shift, end_time=F('end_time') - begin_shift)
            instance.overtime_set.update(start_time=F('start_time') - begin_shift, end_time=F('end_time') - begin_shift)
        instance.begin = request.data['begin']
        instance.end = request.data['end']
        instance.exclude_for_training = request.data.get('exclude_for_training', False)
        if request.data['annotation_status']:
            instance.annotation_status = request.data['annotation_status']
        if instance.annotation_status == 'M':
            instance.fix_switch_end_points()
        game = request.data['game']
        if isinstance(game, dict):
            game = game['id']
        if instance.game.id != game:
            instance.game = models.Game.objects.get(id=game)
        if request.data['attacking_side']:
            instance.attacking_side = request.data['attacking_side']
        s = request.data.get('submap', None)
        if s is not None:
            s = int(s)
        instance.submap_id = s
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
        for k in ['overtime', 'pause', 'replay', 'smaller_window']:
            data[k] = r.get_round_states(k)
        data['point_status'] = r.get_point_status_states()
        data['zoomed_bars'] = r.get_zoomed_bars_states()
        return Response(data)

    @action(methods=['get'], detail=True)
    def kill_feed_items(self, request, pk=None):
        import time
        beg = time.time()
        r = self.get_object()
        print('ROUND GETTING', time.time()-beg)
        beg = time.time()
        kill_feed = r.get_kill_feed_events()
        print('Overall kill feed', time.time()-beg)
        return Response(kill_feed)

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
    def hero_picks(self, request, pk=None):
        round = self.get_object()
        hero_pickes = round.heropick_set.all()
        serializer = serializers.HeroPickDisplaySerializer(hero_pickes, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def kill_feed_events(self, request, pk=None):
        round = self.get_object()
        kills = round.killfeedevent_set.all()
        serializer = serializers.KillFeedEventEditSerializer(kills, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def ultimates(self, request, pk=None):
        round = self.get_object()
        ultimates = round.ultimate_set.all()
        serializer = serializers.UltimateDisplaySerializer(ultimates, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def status_effects(self, request, pk=None):
        round = self.get_object()
        status_effects = round.statuseffect_set.all()
        serializer = serializers.StatusEffectDisplaySerializer(status_effects, many=True)
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

    @action(methods=['get'], detail=True)
    def zooms(self, request, pk=None):
        round = self.get_object()
        zooms = round.zoom_set.all()
        serializer = serializers.ZoomSerializer(zooms, many=True)
        return Response(serializer.data)


class HeroPickViewSet(viewsets.ModelViewSet):
    model = models.HeroPick
    queryset = models.HeroPick.objects.all()
    serializer_class = serializers.HeroPickSerializer

    def create(self, request, *args, **kwargs):
        instance = models.HeroPick.objects.create(time_point=round(request.data['time_point'], 1),
                                                  player_id=request.data['player'], round_id=request.data['round'],
                                                  new_hero_id=request.data['new_hero'])
        instance.round.fix_switch_end_points()
        return Response(self.serializer_class(instance).data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.time_point = request.data['time_point']
        instance.save()
        instance.round.fix_switch_end_points()
        return Response(self.serializer_class(instance).data)

    def destroy(self, request, *args, **kwargs):
        r = self.get_object().round
        resp = super(HeroPickViewSet, self).destroy(request, *args, **kwargs)
        r.fix_switch_end_points()
        return resp


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
        instance.type_id = request.data.get('type', None)
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


class ZoomViewSet(viewsets.ModelViewSet):
    model = models.Zoom
    queryset = models.Zoom.objects.all()
    serializer_class = serializers.ZoomSerializer

    def create(self, request, *args, **kwargs):
        request.data['start_time'] = round(request.data['start_time'], 1)
        end_time = request.data.get('end_time', None)
        if end_time is not None:
            request.data['end_time'] = round(end_time, 1)
        print(request.data)
        return super(ZoomViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.start_time = request.data['start_time']
        instance.end_time = request.data['end_time']
        instance.save()
        return Response()


class KillFeedEventViewSet(viewsets.ModelViewSet):
    model = models.KillFeedEvent
    queryset = models.KillFeedEvent.objects.prefetch_related('ability', 'dying_player').all()
    serializer_class = serializers.KillFeedEventSerializer

    def create(self, request, *args, **kwargs):
        event_type = request.data.pop('event_type')

        request.data['time_point'] = round(request.data['time_point'], 1)
        m = models.KillFeedEvent(round_id=request.data['round'], time_point=request.data['time_point'],
                                 dying_player_id=request.data['dying_player'])
        if event_type in ['kill', 'death'] and request.data.get('dying_npc', None):
            npc = models.NPC.objects.get(pk=request.data['dying_npc'])
            if m.dying_player.get_hero_at_timepoint(m.round, m.time_point) == npc.spawning_hero:
                m.dying_npc = npc
        if event_type in ['kill', 'revive', 'deny']:
            m.killing_player_id = request.data['killing_player']
            m.ability_id = request.data['ability']
        if event_type in ['kill', 'death']:
            m.environmental = request.data.get('environmental', False)
        if event_type == 'kill':
            if m.ability.headshot_capable:
                m.headshot = request.data.get('headshot', False)
        elif event_type == 'deny':
            m.denied_ult_id = request.data['denied_ult']
        m.save()
        return Response(self.serializer_class(m).data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.killing_player is None and request.data.get('killing_player', None):
            instance.killing_player_id = request.data['killing_player']
            instance.ability = models.Ability.objects.get(name='Primary')
        elif request.data.get('killing_player', None):
            instance.killing_player_id = request.data['killing_player']
            instance.ability_id = request.data['ability']['id']
            if instance.ability.headshot_capable:
                instance.headshot = request.data['headshot']
            else:
                instance.headshot = False
        else:
            instance.assists.clear()
            instance.killing_player = None
            instance.ability = None

        instance.environmental = request.data['environmental']
        if request.data['assists']:
            current_assists = instance.assists.all()
            for c in current_assists:
                if c.pk not in request.data['assists']:
                    instance.assists.remove(c)
            current_assists = models.Assist.objects.filter(kill=instance).all()
            assist_ids = [x.player.pk for x in current_assists]
            assist_objects = []
            o = 0
            if current_assists:
                o = current_assists.last().order
            for p in request.data['assists']:
                if p not in assist_ids:
                    o += 1
                    assist_objects.append(models.Assist(player_id=p, kill=instance,order=o))
            if assist_objects:
                models.Assist.objects.bulk_create(assist_objects)
        else:
            instance.assists.clear()

        if request.data.get('dying_npc', None):
            instance.dying_npc_id = request.data['dying_npc']
        else:
            instance.dying_npc = None

        instance.time_point = round(request.data['time_point'], 1)
        instance.save()
        return Response()


class UltimateViewSet(viewsets.ModelViewSet):
    model = models.Ultimate
    queryset = models.Ultimate.objects.prefetch_related('round').all()
    serializer_class = serializers.UltimateSerializer

    def create(self, request, *args, **kwargs):
        request.data['gained'] = round(request.data['gained'], 1)
        return super(UltimateViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.gained = request.data['gained']
        instance.ended = request.data.get('ended', None)
        if request.data.get('used', None):
            use_default = instance.used is None
            instance.used = Decimal(round(request.data['used'], 1)).quantize(Decimal('0.1'))
            if use_default:
                hero = instance.player.get_hero_at_timepoint(instance.round, instance.used)
                instance.ended = hero.ult_duration + instance.used
                if instance.ended > instance.round.duration:
                    instance.ended = instance.round.duration
        else:
            instance.used = request.data.get('used', None)

        instance.save()
        return Response(self.serializer_class(instance).data)

    @action(methods=['PUT'], detail=True)
    def add_use(self, request, *args, **kwargs):
        instance = self.get_object()
        use_default = instance.used is None
        instance.used = Decimal(round(request.data['used'], 1)).quantize(Decimal('0.1'))
        if use_default:
            hero = instance.player.get_hero_at_timepoint(instance.round, instance.used)
            instance.ended = hero.ult_duration + instance.used
            if instance.ended > instance.round.duration:
                instance.ended = instance.round.duration
        instance.save()
        return Response(self.serializer_class(instance).data)

    @action(methods=['PUT'], detail=True)
    def clear_use(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.used = None
        instance.ended = None
        instance.save()
        return Response(self.serializer_class(instance).data)


class StatusEffectViewSet(viewsets.ModelViewSet):
    model = models.StatusEffect
    queryset = models.StatusEffect.objects.all()
    serializer_class = serializers.StatusEffectSerializer

    def create(self, request, *args, **kwargs):
        status_m = models.Status.objects.get(pk=request.data['status'])
        r = models.Round.objects.get(pk=request.data['round'])
        request.data['start_time'] = round(request.data['start_time'], 1)
        request.data['end_time'] = round(request.data['end_time'] + float(status_m.default_duration), 1)
        if request.data['end_time'] > r.duration:
            request.data['end_time'] = r.duration
        print(request.data)
        status_effect = models.StatusEffect.objects.create(start_time=request.data['start_time'],
                                                           end_time=request.data['end_time'],
                                                           round=r,
                                                           player_id=request.data['player'],
                                                           status=status_m
                                                           )

        return Response(self.serializer_class(status_effect).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.start_time = round(request.data['start_time'], 1)
        instance.end_time = round(request.data['end_time'], 1)
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
