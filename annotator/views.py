from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.generic import TemplateView
from django.db.utils import IntegrityError
import os
import json
import re
# Create your views here.


from .utils import scrape_wl
from .models import Event, Match, Player, Team, Map, Game, Round, TeamParticipation, PlayerParticipation, Pause, \
    Unpause, Switch, Kill, Revive, UltGain, UltUse, PointGain, PointFlip, Hero, Death, KillNPC, NPC, NPCDeath
from .forms import TeamForm, PlayerForm, SwitchForm, DeathForm, KillForm, KillNPCForm, NPCDeathForm, PauseForm, \
    PointFlipForm, PointGainForm, UltGainForm, UltUseForm, UnpauseForm, ReviveForm

from .forms import MatchForm

def events_index(request):
    return render(request, 'annotator/event_view.html')

class MatchFormView(TemplateView):
    template_name = "annotator/new_match.html"

    def get_context_data(self, **kwargs):
        context = super(MatchFormView, self).get_context_data(**kwargs)
        context.update(MatchForm=MatchForm())
        return context


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


def index(request):
    return render(request, 'annotator/annotator_app.html')


def import_annotations(request):
    round_data_pattern = r'\d_\d_data.json'
    if False:
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
        t1, _ = Team.objects.get_or_create(name=m_data['team1'], wl_id=int(m_data['team1_id']))
        t2, _ = Team.objects.get_or_create(name=m_data['team2'], wl_id=int(m_data['team2_id']))
        m, _ = Match.objects.get_or_create(wl_id=int(m), event=e, vod=m_data['vod'],
                                           local_location=os.path.join(settings.SCRAPE_CACHE_DIRECTORY, 'matches', m,
                                                                       m + '.mp4'))
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
        for g in os.listdir(match_dir):
            game_dir = os.path.join(match_dir, g)
            print(game_dir)
            if not os.path.isdir(game_dir):
                continue
            json_path = os.path.join(game_dir, 'game{}.json'.format(g))
            if not os.path.exists(json_path):
                continue
            with open(json_path, 'r', encoding='utf8') as f:
                g_data = json.load(f)
            map = Map.objects.get(name__iexact=g_data['map'])
            g, _ = Game.objects.get_or_create(game_number=int(g), match=m, left_points=int(g_data['left_score'][0]),
                                              left_subpoints=g_data['left_score'][1],
                                              right_points=int(g_data['right_score'][0]),
                                              right_subpoints=g_data['right_score'][1], map=map)

            player_mapping = {}
            for f in os.listdir(game_dir):
                if not re.match(round_data_pattern, f):
                    continue
                _, round_num, _ = f.split('_')
                round_num = int(round_num)
                json_path = os.path.join(game_dir, f)
                with open(json_path, 'r', encoding='utf8') as f:
                    r_data = json.load(f)
                if 'blue' in r_data:
                    team_1_color = 'blue'
                    team_2_color = 'red'
                    team_1_color_code = 'B'
                    team_2_color_code = 'R'
                    player1names = 'bluenames'
                    player1IDs = 'blueIDs'
                    player2IDs = 'redIDs'
                    player2names = 'rednames'
                else:
                    player1names = 'leftnames'
                    player1IDs = 'leftIDs'
                    player2IDs = 'rightIDs'
                    player2names = 'rightnames'
                    team_1_color = r_data['leftTeamColor']
                    if team_1_color == 'black':
                        team_1_color_code = 'K'
                    else:
                        team_1_color_code = team_1_color[0].upper()
                    team_2_color = r_data['rightTeamColor']
                    if team_2_color == 'black':
                        team_2_color_code = 'K'
                    else:
                        team_2_color_code = team_2_color[0].upper()
                if round_num == 1:
                    add_team1 = True
                    add_team2 = True
                    for t in g.teamparticipation_set.all():
                        if t.team == t1:
                            add_team1 = False
                            if t.side == 'L':
                                side = 'left'
                            else:
                                side = 'right'
                            for p in t.playerparticipation_set.all():
                                player_mapping[(side, p.player_index)] = p.player
                        elif t.team == t2:
                            add_team2 = False
                            if t.side == 'L':
                                side = 'left'
                            else:
                                side = 'right'
                            for p in t.playerparticipation_set.all():
                                player_mapping[(side, p.player_index)] = p.player
                    participation, _ = TeamParticipation.objects.get_or_create(team=t1, game=g, color=team_1_color_code,
                                                                               side='L')
                    for i, (p_name, p_id) in enumerate(zip(r_data[player1names], r_data[player1IDs])):
                        # print(p_name, p_id)
                        try:
                            p, _ = Player.objects.get_or_create(name=p_name.lower(), wl_id=int(p_id))
                        except IntegrityError:
                            p = Player.objects.get(wl_id=int(p_id))
                            p.name = p_name.lower()
                            p.save()
                        player_participation, _ = PlayerParticipation.objects.get_or_create(player=p,
                                                                                            team_participation=participation,
                                                                                            player_index=i)
                        player_mapping[('left', i)] = p
                    participation, _ = TeamParticipation.objects.get_or_create(team=t2, game=g, color=team_2_color_code,
                                                                               side='R')
                    for i, (p_name, p_id) in enumerate(zip(r_data[player2names], r_data[player2IDs])):
                        # print(p_name, p_id)
                        try:
                            p, _ = Player.objects.get_or_create(name=p_name.lower(), wl_id=int(p_id))
                        except IntegrityError:
                            p = Player.objects.get(wl_id=int(p_id))
                            p.name = p_name.lower()
                            p.save()
                        player_participation, _ = PlayerParticipation.objects.get_or_create(player=p,
                                                                                            team_participation=participation,
                                                                                            player_index=i)
                        player_mapping[('right', i)] = p

                events = r_data['events']
                r, created = Round.objects.get_or_create(round_number=round_num, game=g)
                r.begin = r_data['events'][0][0]
                r.end = r_data['events'][-1][0]
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
                                switches.append(Switch(time_point=time_point, round=r,
                                                       player=player_mapping[(team, player_id)],
                                                       new_hero=hero_cache[h]))
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
                                    if hero is None:
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
                                    if hero is None:
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
                                method = e[7]
                                player = player_mapping[(team, player_id)]
                                hero = player.get_hero_at_timepoint(r, time_point)
                                if hero is None:
                                    hero = Hero.objects.get(name__iexact=transform_wl_heroes('mercy'))
                                ability = None
                                for a in hero.ability_set.all():
                                    if a.name.lower().replace(' ', '') == method:
                                        ability = a
                                        break
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


class MatchInspector(TemplateView):
    template_name = 'annotator/match_view.html'

    def get_context_data(self, **kwargs):
        context = super(MatchInspector, self).get_context_data(**kwargs)
        m = Match.objects.prefetch_related('game_set').get(pk=self.kwargs.get('match_id', None))
        print(m.game_set.all())
        context['match'] = m

        return context


class GameInspector(TemplateView):
    template_name = 'annotator/game_view.html'

    def get_context_data(self, **kwargs):
        context = super(GameInspector, self).get_context_data(**kwargs)

        context['game'] = Game.objects.get(pk=context.get('game_id', None))
        return context


class RoundInspector(TemplateView):
    template_name = 'annotator/round_view.html'

    def get_context_data(self, **kwargs):
        context = super(RoundInspector, self).get_context_data(**kwargs)

        r = Round.objects.prefetch_related('switch_set', 'kill_set', 'npcdeath_set', 'killnpc_set',
                                           'death_set').get(pk=context.get('round_id', None))

        context['switch_form'] = SwitchForm()
        context['death_form'] = DeathForm()
        context['npcdeath_form'] = NPCDeathForm()
        context['kill_form'] = KillForm()
        context['killnpc_form'] = KillNPCForm()
        context['ultgain_form'] = UltGainForm()
        context['ultuse_form'] = UltUseForm()
        context['pause_form'] = PauseForm()
        context['unpause_form'] = UnpauseForm()
        context['pointgain_form'] = PointGainForm()
        context['pointflip_form'] = PointFlipForm()
        context['revive_form'] = ReviveForm()

        context['round'] = r
        context['twitch_id'] = r.get_twitch_id()
        team_participations = r.game.teamparticipation_set.all()
        context['team_form1'] = TeamForm(instance=team_participations[0])
        context['team1_players_form'] = [PlayerForm(instance=x, initial={'order': i}) for i, x in
                                         enumerate(team_participations[0].playerparticipation_set.all())]
        context['team_form2'] = TeamForm(instance=team_participations[1])
        context['team2_players_form'] = [PlayerForm(instance=x, initial={'order': i}) for i, x in
                                         enumerate(team_participations[1].playerparticipation_set.all())]
        return context


def update_team(request):
    if request.method == 'POST':
        game_id = request.POST['game_id']
        side = request.POST['side']
        team_id = request.POST['team_id']
        color = request.POST['color']
        print(request.POST)
        try:
            p = TeamParticipation.objects.get(game__pk=game_id, side=side)
            p.team_id = team_id
            p.color = color
        except TeamParticipation.DoesNotExist:
            p = TeamParticipation(game_id=game_id, team_id=team_id, side=side, color=color)
        p.save()
        return JsonResponse({'success': True})


def delete_event(request):
    if request.method == 'POST':
        event_id = request.POST['event_id']
        event_type = request.POST['event_type']
        types = {'switch': Switch,
                 'kill': Kill,
                 'killnpc': KillNPC,
                 'death': Death,
                 'npcdeath': NPCDeath,
                 'revive': Revive,
                 'ult_gain': UltGain,
                 'ult_use': UltUse,
                 'pause': Pause,
                 'unpause':Unpause,
                 'point_gain': PointGain,
                 'point_flip': PointFlip}
        types[event_type].objects.get(pk=event_id).delete()
        return JsonResponse({'success': True})

def get_current_hero_abilities(request):
    if request.POST:
        player = Player.objects.get(pk=request.POST['player_id'])
        round = Round.objects.get(pk=request.POST['round_id'])
        damaging = request.POST.get('damaging', False)
        damaging = damaging == 'true'
        reviving = request.POST.get('reviving', False)
        reviving = reviving == 'true'
        time_point = int(request.POST['time_point'])
        hero = player.get_hero_at_timepoint(round, time_point)
        abilities = [str(x.pk) for x in hero.ability_set.filter(damaging_ability = damaging, revive_ability=reviving).all()]
        return JsonResponse({'success':True, 'abilities': abilities})

from djng.views.crud import NgCRUDView

class SwitchCRUDView(NgCRUDView):
    model = Switch
