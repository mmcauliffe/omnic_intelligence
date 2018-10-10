from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.generic import TemplateView
from django.db.utils import IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserGroupSerializer, UserWithFullGroupsSerializer, UnauthorizedUserSerializer
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
import os
import requests
import json
import datetime
import re
# Create your views here.
from .utils import scrape_wl, get_stream_channel
from .models import Event, Match, Player, Team, Map, Game, Round, TeamParticipation, PlayerParticipation, Pause, \
    Unpause, Switch, Kill, Revive, UltGain, UltUse, PointGain, PointFlip, Hero, Death, KillNPC, NPC, NPCDeath, \
    StreamVod, StreamChannel


def events_index(request):
    return render(request, 'annotator/event_view.html')


def transform_wl_heroes(hero):
    if hero == 'lucio':
        return 'Lúcio'
    if hero == 'torbjorn':
        return 'Torbjörn'
    if hero == 'dva':
        return 'D.Va'
    if hero == 'soldier76':
        return 'Soldier: 76'
    return hero


def transform_wl_abilities(ability):
    if ability == 'Forge Hammer':
        return 'hammer'
    return ability

def fix_missing_vods():
    rounds = Round.objects.filter(stream_vod=None).all()
    print(rounds)
    for r in rounds:
        if r.vod is not None:
            vod_link = r.vod
        elif r.game.vod is not None:
            vod_link = r.game.vod
        elif r.game.match.vod is not None:
            vod_link = r.game.match.vod
        if r.stream_vod is None:
            youtube_pattern = r'https://(www\.youtube\.com/watch\?v=|youtu\.be/)([-\w]+)'
            youtube_m = re.match(youtube_pattern, vod_link)
            print(youtube_m)
            if youtube_m is not None:
                v = youtube_m.groups()[1]
                print(vod_link)
                print(v)
                response = requests.get(
                    'https://www.googleapis.com/youtube/v3/videos?part=id,snippet&id={video}&key={api_key}'.format(
                        video=v, api_key='AIzaSyCQciF49Br2oZR6bMyg4UQsZ2_iBGv3_tc'))
                if response.status_code != 200:
                    continue
                data = response.json()
                print(data)
                try:
                    data = data['items'][0]['snippet']
                except IndexError:
                    continue
                title = data['title']
                channel_name = data['channelTitle']
                channel, _ = StreamChannel.objects.get_or_create(name=channel_name, site='Y')
                try:
                    published_at = datetime.datetime.strptime(data['publishedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    published_at = datetime.datetime.strptime(data['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                print(title, published_at)

            else:
                twitch_pattern = r'https://www\.twitch\.tv/(\w+)/v/(\d+)'
                twitch_m = re.match(twitch_pattern, vod_link)
                print(vod_link)
                if twitch_m is None:
                    twitch_pattern = r'https://www.twitch.tv/(videos)/(\d+)'
                    twitch_m = re.match(twitch_pattern, vod_link)
                if twitch_m is not None:
                    v = twitch_m.groups()[1]
                    response = requests.get('https://api.twitch.tv/kraken/videos/{}'.format(v),
                                            headers={'Client-ID': 'fgjp7t0f365uazgs84n7t9xhf19xt2'})
                    if response.status_code != 200:
                        continue
                    data = response.json()
                    print(data)
                    title = data['title']
                    try:
                        published_at = datetime.datetime.strptime(data['published_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    except ValueError:
                        published_at = datetime.datetime.strptime(data['published_at'], '%Y-%m-%dT%H:%M:%SZ')

                    channel_name = data['channel']['name']
                    channel, _ = StreamChannel.objects.get_or_create(name=channel_name, site='T')
            try:
                vod = StreamVod.objects.get(url=vod_link)
                vod.channel = channel
                vod.title = title
                vod.broadcast_date = published_at
                vod.save()
            except StreamVod.DoesNotExist:
                vod, c = StreamVod.objects.get_or_create(channel=channel, url=vod_link, title=title,
                                                         broadcast_date=published_at)

            r.stream_vod = vod
        r.save()

def index(request):
    return render(request, 'annotator/annotator_app.html')


def check_channel(request, channel_id):
    c = StreamChannel.objects.prefetch_related('streamvod_set').get(pk=channel_id)
    print(c)
    if c.site == 'T':
        response = requests.get('https://api.twitch.tv/helix/users?login={}'.format(c.name),
                                headers={'Client-ID': 'fgjp7t0f365uazgs84n7t9xhf19xt2'})
        data = response.json()['data'][0]
        id = data['id']
        print(id)
        cursor = ''
        while True:
            vod_urls = [x.url for x in c.streamvod_set.all()]
            vods = []
            if not cursor:
                response = requests.get('https://api.twitch.tv/helix/videos?user_id={}'.format(id),
                                        headers={'Client-ID': 'fgjp7t0f365uazgs84n7t9xhf19xt2'})
            else:
                response = requests.get('https://api.twitch.tv/helix/videos?user_id={}&first=100&after={}'.format(id, cursor),
                                        headers={'Client-ID': 'fgjp7t0f365uazgs84n7t9xhf19xt2'})

            data = response.json()
            try:
                cursor = data['pagination']['cursor']
            except KeyError:
                break
            print(data.keys())
            data = data['data']
            for v in data:
                title = v['title']
                if 'Game' not in title:
                    continue
                broadcast_date = v['published_at']
                url = v['url']
                if url in vod_urls:
                    continue
                vod_urls.append(url)
                vods.append(StreamVod(title=title, url=url, broadcast_date=broadcast_date, channel=c))
                print(v)
            StreamVod.objects.bulk_create(vods)
    return HttpResponse(status=200)

def export_round(request, round_id):
    r = Round.objects.get(pk=round_id)
    annotations = r.for_wl()

    response = HttpResponse(json.dumps(annotations), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename={}_{}_{}.json'.format(r.game.match.wl_id,
                                                                                  r.game.game_number, r.round_number)

    return response


def import_annotations(request):
    round_data_pattern = r'\d_\d_data.json'
    if False:
        print('beginning scraping!')
        scrape_wl()
    hero_cache = {}
    npc_cache = {}
    matches_dir = os.path.join(settings.SCRAPE_CACHE_DIRECTORY, 'matches')
    for m in sorted(os.listdir(matches_dir), key=lambda x: int(x)):

        print(m)
        match_dir = os.path.join(matches_dir, m)
        json_path = os.path.join(match_dir, '{}.json'.format(m))
        if not os.path.exists(json_path):
            continue
        with open(json_path, 'r', encoding='utf8') as f:
            m_data = json.load(f)
        e, _ = Event.objects.get_or_create(name=m_data['event'], wl_id=int(m_data['event_id']))
        if False and 'event_channel' not in m_data:
            s = get_stream_channel(m_data['event_id'])
            if s is not None:
                m_data['event_channel'] = s[0]
                m_data['event_channel_link'] = s[1]
            else:
                m_data['event_channel'] = ''
                m_data['event_channel_link'] = ''
        #channel, _ = StreamChannel.objects.get_or_create(name=m_data['event_channel'], site='T')
        t1, _ = Team.objects.get_or_create(name=m_data['team1'], wl_id=int(m_data['team1_id']))
        t2, _ = Team.objects.get_or_create(name=m_data['team2'], wl_id=int(m_data['team2_id']))
        m, created = Match.objects.get_or_create(wl_id=int(m), event=e)
        if created:
            m.vod = m_data['vod']
        m_teams = m.teams.all()
        for t in m_teams:
            if t == t1:
                break
        else:
            m.teams.add(t1)
        for t in m_teams:
            if t == t2:
                break
        else:
            m.teams.add(t2)
        m.save()
        for g in os.listdir(match_dir):
            game_dir = os.path.join(match_dir, g)
            print(game_dir)
            if not os.path.isdir(game_dir):
                print(game_dir + ' does not exist')
                continue
            json_path = os.path.join(game_dir, 'game{}.json'.format(g))
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf8') as f:
                    g_data = json.load(f)
            else:
                g_data = {'left_score': [0, ''], 'right_score': [0, ''], 'map': ''}
            meta_path = os.path.join(game_dir, 'meta.json')
            if not os.path.exists(meta_path):
                r1_path = os.path.join(game_dir, '{}_1_data.json'.format(g))
                if os.path.exists(r1_path):
                    with open(r1_path, 'r', encoding='utf8') as f:
                        meta_data = json.load(f)
                        del meta_data['events']
                        del meta_data['picks']
                else:
                    try:
                        os.remove(game_dir)
                    except:
                        pass
                    print(meta_path + ' does not exist')
                    continue
            else:
                with open(meta_path, 'r', encoding='utf8') as f:
                    meta_data = json.load(f)
            if 'map' in meta_data and meta_data['map']:
                map = Map.objects.get(name__iexact=meta_data['map'])
            elif g_data['map']:
                map = Map.objects.get(name__iexact=g_data['map'])
            else:
                print('Lack of map')
                print(meta_data)
                print(g_data)
                continue
            if 'blue' in meta_data:
                source = 'W'
                team_1_color = 'blue'
                team_2_color = 'red'
                team_1_color_code = 'B'
                team_2_color_code = 'R'
                player1names = 'bluenames'
                player1IDs = 'blueIDs'
                player2IDs = 'redIDs'
                player2names = 'rednames'
                left_team, _ = Team.objects.get_or_create(name=meta_data[team_1_color].lower(),
                                                          wl_id=meta_data['blueTeamID'])
                right_team, _ = Team.objects.get_or_create(name=meta_data[team_2_color].lower(),
                                                           wl_id=meta_data['redTeamID'])
            else:
                source = 'M'
                player1names = 'leftnames'
                player1IDs = 'leftIDs'
                player2IDs = 'rightIDs'
                player2names = 'rightnames'
                try:
                    team_1_color = meta_data['leftTeamColor']
                except KeyError:
                    continue
                if team_1_color == 'black':
                    team_1_color_code = 'K'
                else:
                    team_1_color_code = team_1_color[0].upper()
                team_2_color = meta_data['rightTeamColor']
                if team_2_color == 'black':
                    team_2_color_code = 'K'
                else:
                    team_2_color_code = team_2_color[0].upper()
                left_team, _ = Team.objects.get_or_create(name=meta_data['left'].lower(), wl_id=meta_data['leftTeamID'])
                right_team, _ = Team.objects.get_or_create(name=meta_data['right'].lower(),
                                                           wl_id=meta_data['rightTeamID'])
            if left_team.wl_id not in [x.wl_id for x in m.teams.all()]:
                print(game_dir)
                print(left_team.name, left_team.wl_id, m.teams.all(), [x.wl_id for x in m.teams.all()])
                raise Exception

            player_mapping = {}
            try:
                g = Game.objects.get(game_number=int(g), match=m)
                print('found game!')
                for p in g.left_team.playerparticipation_set.all():
                    player_mapping[('left', p.player_index)] = p.player
                for p in g.right_team.playerparticipation_set.all():
                    player_mapping[('right', p.player_index)] = p.player
            except Game.DoesNotExist:
                left_team_participation = TeamParticipation.objects.create(team=left_team, color=team_1_color_code,
                                                                           points=int(g_data['left_score'][0]),
                                                                           subpoints=g_data['left_score'][1])
                for i, (p_name, p_id) in enumerate(zip(meta_data[player1names], meta_data[player1IDs])):
                    try:
                        p, _ = Player.objects.get_or_create(name=p_name.lower(), wl_id=int(p_id))
                    except IntegrityError:
                        p = Player.objects.get(wl_id=int(p_id))
                        p.name = p_name.lower()
                        p.save()
                    player_participation, _ = PlayerParticipation.objects.get_or_create(player=p,
                                                                                        team_participation=left_team_participation,
                                                                                        player_index=i)
                    player_mapping[('left', i)] = p
                right_team_participation = TeamParticipation.objects.create(team=right_team, color=team_2_color_code,
                                                                            points=int(g_data['right_score'][0]),
                                                                            subpoints=g_data['right_score'][1])
                for i, (p_name, p_id) in enumerate(zip(meta_data[player2names], meta_data[player2IDs])):
                    try:
                        p, _ = Player.objects.get_or_create(name=p_name.lower(), wl_id=int(p_id))
                    except IntegrityError:
                        p = Player.objects.get(wl_id=int(p_id))
                        p.name = p_name.lower()
                        p.save()
                    player_participation, _ = PlayerParticipation.objects.get_or_create(player=p,
                                                                                        team_participation=right_team_participation,
                                                                                        player_index=i)
                    player_mapping[('right', i)] = p

                g = Game.objects.create(game_number=int(g), match=m, map=map, left_team=left_team_participation,
                                        right_team=right_team_participation)
                print('created game!')

            vods = set()
            for f in os.listdir(game_dir):
                if not re.match(round_data_pattern, f):
                    continue
                _, round_num, _ = f.split('_')
                round_num = int(round_num)
                json_path = os.path.join(game_dir, f)
                with open(json_path, 'r', encoding='utf8') as f:
                    r_data = json.load(f)
                if 'base_url' not in r_data:
                    continue
                vods.add(r_data['base_url'])
            add_round_vod = len(vods) > 1
            if not add_round_vod and len(vods) > 0:
                g.vod = list(vods)[0]
            for f in os.listdir(game_dir):
                if not re.match(round_data_pattern, f):
                    continue
                _, round_num, _ = f.split('_')
                round_num = int(round_num)
                json_path = os.path.join(game_dir, f)
                with open(json_path, 'r', encoding='utf8') as f:
                    r_data = json.load(f)
                events = r_data['events']
                r, created = Round.objects.get_or_create(round_number=round_num, game=g)
                c = False
                if r.stream_vod is None:
                    if 'base_url' in r_data:
                        vod_link = r_data['base_url']
                    elif 'youtube' in r_data:
                        vod_link = 'https://www.youtube.com/watch?v={}'.format(r_data['youtube'])
                    youtube_pattern = r'https://(www\.youtube\.com/watch\?v=|youtu\.be/)([-\w]+)'
                    youtube_m = re.match(youtube_pattern, vod_link)
                    print(youtube_m)
                    if youtube_m is not None:
                        v = youtube_m.groups()[1]
                        print(vod_link)
                        print(v)
                        response = requests.get('https://www.googleapis.com/youtube/v3/videos?part=id,snippet&id={video}&key={api_key}'.format(video=v, api_key='AIzaSyCQciF49Br2oZR6bMyg4UQsZ2_iBGv3_tc'))
                        if response.status_code != 200:
                            continue
                        data = response.json()
                        print(data)
                        try:
                            data = data['items'][0]['snippet']
                        except IndexError:
                            continue
                        title = data['title']
                        channel_name = data['channelTitle']
                        channel, _ = StreamChannel.objects.get_or_create(name = channel_name, site='Y')
                        try:
                            published_at = datetime.datetime.strptime(data['publishedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                        except ValueError:
                            published_at = datetime.datetime.strptime(data['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                        print(title, published_at)

                    else:
                        twitch_pattern = r'https://www\.twitch\.tv/(\w+)/v/(\d+)'
                        twitch_m = re.match(twitch_pattern, vod_link)
                        print(vod_link)
                        if twitch_m is None:
                            twitch_pattern = r'https://www.twitch.tv/(videos)/(\d+)'
                            twitch_m = re.match(twitch_pattern, vod_link)
                        if twitch_m is not None:
                            v = twitch_m.groups()[1]
                            response = requests.get('https://api.twitch.tv/kraken/videos/{}'.format(v), headers={'Client-ID': 'fgjp7t0f365uazgs84n7t9xhf19xt2'})
                            if response.status_code != 200:
                                continue
                            data = response.json()
                            print(data)
                            title = data['title']
                            try:
                                published_at = datetime.datetime.strptime(data['published_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                            except ValueError:
                                published_at = datetime.datetime.strptime(data['published_at'], '%Y-%m-%dT%H:%M:%SZ')

                            channel_name = data['channel']['name']
                            channel, _ = StreamChannel.objects.get_or_create(name = channel_name, site='T')
                    try:
                        vod = StreamVod.objects.get(url=vod_link)
                        vod.channel = channel
                        vod.title = title
                        vod.broadcast_date = published_at
                        vod.save()
                    except StreamVod.DoesNotExist:
                        vod, c = StreamVod.objects.get_or_create(channel=channel, url=vod_link, title=title, broadcast_date=published_at)

                    r.stream_vod = vod
                r.save()
                if 'blue' in r_data and set(r_data['blueIDs']) != set(meta_data[player1IDs]):
                    print(game_dir)
                    print(r_data['blueIDs'], meta_data[player1IDs])
                    print(r_data['bluenames'], meta_data[player1names])
                    print(r_data['rednames'], meta_data[player2names])
                    print(r_data['blue'], r_data['red'])
                    print(meta_data['blue'], meta_data['red'])
                    r.delete()
                    raise Exception
                if created:
                    r.begin = r_data['events'][0][0]
                    r.end = r_data['events'][-1][0]
                    r.annotation_status = source
                add_swithes = r.switch_set.count() == 0
                add_killnpcs = r.killnpc_set.count() == 0
                add_kills = r.kill_set.count() == 0
                add_deaths = r.death_set.count() == 0
                add_npcdeaths = r.npcdeath_set.count() == 0
                add_revives = r.revive_set.count() == 0
                add_pointflips = r.pointflip_set.count() == 0
                add_pointgains = r.pointgain_set.count() == 0
                add_pauses = r.pause_set.count() == 0
                add_unpauses = r.unpause_set.count() == 0
                add_ultgains = r.ultgain_set.count() == 0
                add_ultuses = r.ultuse_set.count() == 0
                print(r.switch_set.count(), r.kill_set.count(), r.death_set.count())
                if add_swithes or add_killnpcs or add_kills or add_deaths \
                        or add_npcdeaths or add_revives or add_pointflips \
                        or add_pointgains or add_pauses == 0 or add_unpauses or add_ultgains or add_ultuses:
                    point_flips = []
                    point_gains = []
                    pauses = []
                    unpauses = []
                    switches = []
                    deaths = []
                    npcdeaths = []
                    ultgains = []
                    ultuses = []
                    kills = []
                    killnpcs = []
                    revives = []
                    if events[1][1] == 'ATTACK':
                        if events[1][2].lower() == team_1_color:
                            r.attacking_side = 'L'
                        else:
                            r.attacking_side = 'R'
                    r.save()
                    switch_set = set()
                    death_set = set()
                    npc_death_set = set()
                    kill_set = set()
                    kill_npc_set = set()
                    point_flip_set = set()
                    point_gain_set = set()
                    pause_set = set()
                    unpause_set = set()
                    revive_set = set()
                    for e in r_data['events']:
                        time_point = e[0] - r.begin
                        event_type = e[1]

                        if event_type in ['MATCH', 'END']:
                            continue
                        if r.attacking_side != 'N' and event_type == 'ATTACK':
                            continue
                        if event_type == 'ATTACK' and add_pointflips:
                            team = e[2].lower()
                            if team == team_1_color:
                                team = 'L'
                            else:
                                team = 'R'
                            if time_point not in point_flip_set:
                                point_flips.append(PointFlip(time_point=time_point, round=r, controlling_side=team))
                                point_flip_set.add(time_point)
                        elif event_type == 'POINTS' and add_pointgains:
                            try:
                                points = int(e[-1])
                            except ValueError:
                                points = 0
                            if time_point not in point_gain_set:
                                point_gains.append(PointGain(time_point=time_point, round=r, point_total=points))
                                point_gain_set.add(time_point)
                        elif event_type == 'PAUSE' and add_pauses:
                            if time_point not in pause_set:
                                pauses.append(Pause(time_point=time_point, round=r))
                                pause_set.add(time_point)
                        elif event_type == 'UNPAUSE' and add_unpauses:
                            if time_point not in unpause_set:
                                unpauses.append(Unpause(time_point=time_point, round=r))
                                unpause_set.add(time_point)
                        elif event_type in ['SWITCH', 'DEATH', 'ULT_GAIN', 'ULT_USE', 'KILL', 'REVIVE']:
                            team = e[2].lower()
                            if team == team_1_color:
                                team = 'left'
                            else:
                                team = 'right'
                            player_id = int(e[3]) - 1
                            if event_type == 'SWITCH' and add_swithes:
                                h = e[-1]
                                if h not in hero_cache and h != '':
                                    print(h)
                                    hero_cache[h] = Hero.objects.get(name__iexact=transform_wl_heroes(h))
                                elif h == '':
                                    hero_cache[h] = None
                                if (time_point, player_mapping[(team, player_id)], hero_cache[h]) not in switch_set:
                                    switches.append(Switch(time_point=time_point, round=r,
                                                       player=player_mapping[(team, player_id)],
                                                       new_hero=hero_cache[h]))
                                    switch_set.add((time_point, player_mapping[(team, player_id)], hero_cache[h]))
                            elif event_type == 'DEATH' and add_deaths:
                                if (time_point, player_mapping[(team, player_id)]) not in death_set:
                                    deaths.append(Death(time_point=time_point, round=r,
                                                        player=player_mapping[(team, player_id)]))
                                    death_set.add((time_point, player_mapping[(team, player_id)]))
                            elif event_type == 'ULT_GAIN' and add_ultgains:
                                ultgains.append(UltGain(time_point=time_point, round=r,
                                                        player=player_mapping[(team, player_id)]))
                            elif event_type == 'ULT_USE' and add_ultuses:
                                ultuses.append(UltUse(time_point=time_point, round=r,
                                                      player=player_mapping[(team, player_id)]))
                            elif event_type == 'KILL' and (add_kills or add_killnpcs):
                                killed_id = int(e[5]) - 1
                                if team == 'left':
                                    killed_team = 'right'
                                else:
                                    killed_team = 'left'
                                try:
                                    method = e[7]
                                    headshot = e[8] == 'headshot'
                                except IndexError:
                                    method = 'primary'
                                    headshot = False
                                if method == 'headshot':
                                    method = 'primary'
                                    headshot = True
                                if not method:
                                    method = 'primary'
                                if player_id < 0:
                                    print(e)
                                    if switches:
                                        Switch.objects.bulk_create(switches)
                                        switches = []
                                    for k, p in player_mapping.items():
                                        hero = p.get_hero_at_timepoint(r, time_point)
                                        if e[4] == 'mech' and hero.name == 'D.Va':
                                            player = p
                                            break
                                else:
                                    player = player_mapping[(team, player_id)]
                                if killed_id < 0 and add_killnpcs:
                                    print(e)
                                    hero = player.get_hero_at_timepoint(r, time_point)
                                    if not hero:
                                        hero = Hero.objects.get(name__iexact=transform_wl_heroes(e[4]))
                                    ability = None
                                    for a in hero.ability_set.all():
                                        looking_for = transform_wl_abilities(a.name).lower().replace(' ', '').replace(
                                            '-', '').replace(':', '')
                                        print(looking_for)
                                        if method == 'helixrocket':
                                            method = 'helixrockets'
                                        elif method == 'selfjerruct':
                                            method = 'selfdestruct'
                                        elif method == 'regular':
                                            method = 'primary'
                                        if looking_for == method:
                                            ability = a
                                            break
                                    if ability is None:
                                        print(method, ability)
                                        raise Exception
                                    npc = e[6]
                                    if npc not in npc_cache:
                                        npc_cache[npc] = NPC.objects.get(name__iexact=npc)
                                    if (time_point, player, npc_cache[npc]) not in kill_npc_set:
                                        killnpcs.append(KillNPC(time_point=time_point, round=r, killing_player=player,
                                                                killed_npc=npc_cache[npc], ability=ability))
                                        kill_npc_set.add((time_point, player, npc_cache[npc]))
                                    if (time_point, npc_cache[npc]) not in npc_death_set and add_npcdeaths:
                                        npcdeaths.append(NPCDeath(time_point=time_point, round=r, npc=npc_cache[npc]))
                                        npc_death_set.add((time_point, npc_cache[npc]))
                                elif add_kills:
                                    print(e)
                                    hero = player.get_hero_at_timepoint(r, time_point)
                                    if not hero:
                                        hero = Hero.objects.get(name__iexact=transform_wl_heroes(e[4]))
                                    ability = None
                                    for a in hero.ability_set.all():
                                        looking_for = transform_wl_abilities(a.name).lower().replace(' ', '').replace(
                                            '-', '').replace(':', '')
                                        print(looking_for)
                                        if method == 'helixrocket':
                                            method = 'helixrockets'
                                        elif method == 'selfjerruct':
                                            method = 'selfdestruct'
                                        elif method == 'regular':
                                            method = 'primary'
                                        if looking_for == method:
                                            ability = a
                                            break
                                    if ability is None:
                                        print(method, ability)
                                        raise Exception
                                    if (time_point, player, player_mapping[(killed_team, killed_id)]) not in kill_set:
                                        kills.append(Kill(time_point=time_point, round=r, killing_player=player,
                                                          killed_player=player_mapping[(killed_team, killed_id)],
                                                          ability=ability, headshot=headshot))
                                        kill_set.add((time_point, player, player_mapping[(killed_team, killed_id)]))
                                    if (time_point,
                                        player_mapping[(killed_team, killed_id)]) not in death_set and add_deaths:
                                        deaths.append(Death(time_point=time_point, round=r,
                                                            player=player_mapping[(killed_team, killed_id)]))
                                        death_set.add((time_point, player_mapping[(killed_team, killed_id)]))
                            elif event_type == 'REVIVE' and add_revives:
                                revived_id = int(e[5]) - 1
                                try:
                                    method = e[7]
                                except:
                                    method = 'resurrect'
                                print(method)
                                player = player_mapping[(team, player_id)]
                                hero = player.get_hero_at_timepoint(r, time_point)
                                print(hero)
                                if not hero:
                                    hero = Hero.objects.get(name__iexact=transform_wl_heroes('mercy'))
                                ability = None
                                for a in hero.ability_set.all():
                                    if a.name.lower().replace(' ', '') == method:
                                        ability = a
                                        break
                                    elif a.name.lower() == 'resurrect':
                                        ability = a
                                if (time_point, player, player_mapping[(team, revived_id)]) not in revive_set:
                                    revives.append(Revive(time_point=time_point, round=r, reviving_player=player,
                                                          revived_player=player_mapping[(team, revived_id)],
                                                          ability=ability))
                                    revive_set.add((time_point, player, player_mapping[(team, revived_id)]))
                    if switches:
                        Switch.objects.bulk_create(switches)
                    if deaths:
                        Death.objects.bulk_create(deaths)
                    if npcdeaths:
                        NPCDeath.objects.bulk_create(npcdeaths)
                    if kills:
                        Kill.objects.bulk_create(kills)
                    if killnpcs:
                        KillNPC.objects.bulk_create(killnpcs)
                    if revives:
                        Revive.objects.bulk_create(revives)
                    if ultgains:
                        UltGain.objects.bulk_create(ultgains)
                    if ultuses:
                        UltUse.objects.bulk_create(ultuses)
                    if point_gains:
                        PointGain.objects.bulk_create(point_gains)
                    if point_flips:
                        PointFlip.objects.bulk_create(point_flips)
                    if pauses:
                        Pause.objects.bulk_create(pauses)
                    if unpauses:
                        Unpause.objects.bulk_create(unpauses)

    return HttpResponse(status=200)


class CheckAuthView(generics.views.APIView):
    def get(self, request, *args, **kwargs):
        print(request.user)
        if isinstance(request.user, User):
            return Response(UserWithFullGroupsSerializer(request.user).data)
        else:
            return Response(UnauthorizedUserSerializer(request.user).data)

class AuthView(generics.views.APIView):

    def post(self, request, *args, **kwargs):
        print(request.data)
        print(dir(request))
        print(dir(request.session))

        user = authenticate(request, username=request.data['username'], password=request.data['password'])
        login(request, user)
        return Response(UserWithFullGroupsSerializer(request.user).data)

    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response({})
