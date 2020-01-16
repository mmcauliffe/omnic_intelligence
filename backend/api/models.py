from django.db import models
import os
import re
import csv
from decimal import Decimal
from django.conf import settings
import subprocess
from collections import Counter
from colorful.fields import RGBColorField
from django.db.models import Q

LEFT = 'L'
RIGHT = 'R'
NEITHER = 'N'
SIDE_CHOICES = (
    (LEFT, 'Left'),
    (RIGHT, 'Right'),
    (NEITHER, 'Neither'),
)

ORIGINAL = 'O'
FILM_FORMAT_CHOICES = ((ORIGINAL, 'Original'),
                       ('W', 'World Cup 2017'),
                       ('A', 'APEX'),
                       ('1', 'Korean Contenders season 1'),
                       ('K', 'Korean Contenders season 2'),
                       ('U', 'Australia Contenders season 2'),
                       ('G', 'Gauntlet 2019'),
                       ('2', 'Overwatch league season 2'))

# Create your models here.

class Patch(models.Model):
    version_number = models.CharField(max_length=128, unique=True)
    live_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)


class StreamChannel(models.Model):
    SITE_CHOICES = (('T', 'Twitch'),
                    ('Y', 'YouTube'))
    name = models.CharField(max_length=256, unique=True)
    site = models.CharField(max_length=1, choices=SITE_CHOICES, default='T')
    youtube_channel_id = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.get_site_display())


class StreamVod(models.Model):
    STATUS_CHOICES = (
        ('N', 'Not analyzed'),
        ('G', 'Automatically annotated for in-game/out-of-game'),
        ('T', 'Game boundaries manually checked'),
        ('A', 'Rounds automatically annotated'),
        ('M', 'Round events manually corrected')
                      )
    MATCH_TYPE = 'M'
    GAME_TYPE = 'G'
    TYPE_CHOICES = (
        (MATCH_TYPE, 'Match'),
        (GAME_TYPE, 'Game'),
        ('R', 'Round')
    )
    channel = models.ForeignKey(StreamChannel, on_delete=models.CASCADE)
    url = models.URLField(max_length=256, unique=True)
    title = models.CharField(max_length=256)
    broadcast_date = models.DateTimeField(blank=True, null=True)
    film_format = models.CharField(max_length=1, choices=FILM_FORMAT_CHOICES, default=ORIGINAL)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N')
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='M')
    last_modified = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def rounds(self):
        rounds = self.round_set.prefetch_related('game', 'game__match').all()
        return rounds

    @property
    def event(self):
        events = self.channel.events.filter(end_date__gte=self.broadcast_date, start_date__lte=self.broadcast_date).all()
        for e in events:
            if e.channel_query_string is not None:
                if e.channel_query_string not in self.title:
                    continue
            return e
        return None

    @property
    def games(self):
        rounds = self.rounds
        games = []
        for r in rounds:
            for g in r.game.match.game_set.all():
                if g not in games:
                    games.append(g)
        return games

    @property
    def matches(self):
        games = self.games
        matches = []
        for g in games:
            if g.match not in matches:
                matches.append(g.match)
        return matches

    @property
    def sequences(self):
        rounds = self.round_set.order_by('begin').all()
        sequences = []
        for r in rounds:
            sequences.append([r.begin, r.end])
        return sequences

    @property
    def vod_link(self):
        m = re.match(r'https://www\.twitch\.tv/videos/(\d+)[?]?.*', self.url)
        if m is not None:
            return 'twitch', m.groups()[0]
        m = re.search(r'https://www\.youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})', self.url)
        if m is not None:
            return 'youtube', m.groups()[0]
        m = re.search(r'https://youtu\.be/([a-zA-Z0-9_-]{11})', self.url)
        if m is not None:
            return 'youtube', m.groups()[0]

    def get_status(self):
        rounds = self.round_set.prefetch_related('game', 'game__match', 'game__match__event',
                                                'pause_set', 'replay_set', 'smallerwindow_set', 'zoom_set').all()
        return_dict = {'game': [],
                       'spectator_mode': [],
                       'film_format': [],
                       'left_color': [],
                       'right_color': [],
                       'map': [],
                       'submap': [],
                       'attacking_side': [],
                       'left': [],
                       'right': []
                       }
        for r in rounds:
            statuses = []
            lefts = []
            rights = []
            b = Decimal('0.0')
            spectator_mode = r.game.match.event.get_spectator_mode_display().lower()
            film_format = r.game.match.event.get_film_format_display().lower()
            m = r.game.map
            map_name = m.name.lower()
            left_color = r.game.left_team.get_color_display().lower()
            right_color = r.game.right_team.get_color_display().lower()
            if return_dict['game']:
                b = return_dict['game'][-1]['end']
            return_dict['game'].append({'begin': b, 'end': r.begin, 'status': 'not_game'})
            return_dict['film_format'].append({'begin': b, 'end': r.begin, 'status': 'n/a'})
            return_dict['map'].append({'begin': b, 'end': r.begin, 'status': 'n/a'})
            return_dict['submap'].append({'begin': b, 'end': r.begin, 'status': 'n/a'})
            return_dict['attacking_side'].append({'begin': b, 'end': r.begin, 'status': 'n/a'})
            return_dict['left_color'].append({'begin': b, 'end': r.begin, 'status': 'n/a'})
            return_dict['right_color'].append({'begin': b, 'end': r.begin, 'status': 'n/a'})
            return_dict['spectator_mode'].append({'begin': b, 'end': r.begin, 'status': 'n/a'})
            return_dict['left'].append({'begin': b, 'end': r.begin, 'status': 'n/a'})
            return_dict['right'].append({'begin': b, 'end': r.begin, 'status': 'n/a'})
            for p in r.pause_set.all():
                statuses.append({'begin': r.begin + p.start_time, 'end': r.begin + p.end_time, 'status': 'pause'})
            for p in r.replay_set.all():
                statuses.append({'begin': r.begin + p.start_time, 'end': r.begin + p.end_time, 'status': 'replay'})
            for p in r.smallerwindow_set.all():
                statuses.append(
                    {'begin': r.begin + p.start_time, 'end': r.begin + p.end_time, 'status': 'smaller_window'})

            return_dict['spectator_mode'].append({'begin': r.begin, 'end': r.end, 'status': spectator_mode})
            return_dict['film_format'].append({'begin': r.begin, 'end': r.end, 'status': film_format})
            return_dict['map'].append({'begin': r.begin, 'end': r.end, 'status': map_name})
            if r.submap is not None:
                return_dict['submap'].append({'begin': r.begin, 'end': r.end, 'status': r.submap.display_name.lower()})
            else:
                for p in r.get_point_status_states():
                    return_dict['submap'].append({'begin': r.begin + p['begin'], 'end': r.begin + p['end'],
                                                  'status': map_name + '_' + p['status'].split('_')[-1]})

            return_dict['attacking_side'].append({'begin': r.begin, 'end': r.end, 'status': r.get_attacking_side_display().lower()})
            return_dict['left_color'].append({'begin': r.begin, 'end': r.end, 'status': left_color})
            return_dict['right_color'].append({'begin': r.begin, 'end': r.end, 'status': right_color})
            if not statuses:
                return_dict['game'].append({'begin': r.begin, 'end': r.end, 'status': 'game'})
            else:
                for s in sorted(statuses, key=lambda x: x['begin']):
                    b = return_dict['game'][-1]['end']
                    if b != s['begin']:
                        return_dict['game'].append({'begin': b, 'end': s['begin'], 'status': 'game'})
                    return_dict['game'].append(s)
                if return_dict['game'][-1]['end'] != r.end:
                    return_dict['game'].append(
                        {'begin': return_dict['game'][-1]['end'], 'end': r.end, 'status': 'game'})
            for p in r.zoom_set.all():
                if p.side == 'L':
                    lefts.append({'begin': r.begin + p.start_time, 'end': r.begin + p.end_time, 'status': 'zoom'})
                else:
                    rights.append({'begin': r.begin + p.start_time, 'end': r.begin + p.end_time, 'status': 'zoom'})

            if not lefts:
                return_dict['left'].append({'begin': r.begin, 'end': r.end, 'status': 'not_zoom'})
            else:
                for s in lefts:
                    b = return_dict['left'][-1]['end']
                    if b != s['begin']:
                        return_dict['left'].append({'begin': b, 'end': s['begin'], 'status': 'not_zoom'})
                    return_dict['left'].append(s)
                if return_dict['left'][-1]['end'] != r.end:
                    return_dict['left'].append(
                        {'begin': return_dict['left'][-1]['end'], 'end': r.end, 'status': 'not_zoom'})

            if not rights:
                return_dict['right'].append({'begin': r.begin, 'end': r.end, 'status': 'not_zoom'})
            else:
                for s in rights:
                    b = return_dict['right'][-1]['end']
                    if b != s['begin']:
                        return_dict['right'].append({'begin': b, 'end': s['begin'], 'status': 'not_zoom'})
                    return_dict['right'].append(s)
                if return_dict['right'][-1]['end'] != r.end:
                    return_dict['right'].append(
                        {'begin': return_dict['right'][-1]['end'], 'end': r.end, 'status': 'not_zoom'})
        return return_dict


class Map(models.Model):
    MODE_CHOICES = (
        ('A', 'Assault'),
        ('E', 'Escort'),
        ('C', 'Control'),
        ('H', 'Hybrid')
    )
    name = models.CharField(max_length=128, unique=True)
    mode = models.CharField(max_length=1, choices=MODE_CHOICES)

    def __str__(self):
        return self.name


class Submap(models.Model):
    name = models.CharField(max_length=128, unique=True)
    map = models.ForeignKey(Map, on_delete=models.CASCADE)

    @property
    def display_name(self):
        return self.map.name + '_' + self.name


class Hero(models.Model):
    DAMAGE = 'D'
    TANK = 'T'
    SUPPORT = 'S'
    TYPE_CHOICES = (
        (DAMAGE, 'Damage'),
        (TANK, 'Tank'),
        (SUPPORT, 'Support'),
    )
    name = models.CharField(max_length=128, unique=True)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    ult_duration = models.DecimalField(max_digits=6, decimal_places=1, default=Decimal('1.0'))

    class Meta:
        verbose_name_plural = "heroes"
        ordering = ['type', 'name']

    def __str__(self):
        return self.name

    @property
    def ability_denier(self):
        return self.abilities.filter(type=Ability.DENYING_TYPE).count() > 0


class Status(models.Model):
    name = models.CharField(max_length=128, unique=True)
    independent = models.BooleanField(default=False)
    helpful = models.BooleanField(default=False)
    causing_hero = models.ForeignKey(Hero, on_delete=models.CASCADE, null=True, blank=True)
    default_duration = models.DecimalField(max_digits=6, decimal_places=1, default=Decimal('1.0'))

    class Meta:
        verbose_name_plural = "statuses"

    def __str__(self):
        return self.name


class NPC(models.Model):
    name = models.CharField(max_length=128, unique=True)
    spawning_hero = models.ForeignKey(Hero, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "NPC"
        verbose_name_plural = "NPCs"

    def __str__(self):
        return self.name


class Ability(models.Model):
    DAMAGING_TYPE = 'D'
    REVIVING_TYPE = 'R'
    DENYING_TYPE = 'E'
    ABILITY_TYPES = ((DAMAGING_TYPE, 'Damaging'),
                     (REVIVING_TYPE, 'Reviving'),
                     (DENYING_TYPE, 'Denying'))
    heroes = models.ManyToManyField(Hero, related_name='abilities')
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=1, choices=ABILITY_TYPES, default=DAMAGING_TYPE)
    headshot_capable = models.BooleanField(default=False)
    ultimate = models.BooleanField(default=False)
    deniable = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "abilities"
        ordering = ['name']

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=128)
    liquipedia_id = models.CharField(max_length=128, null=True, blank=True)
    owl_id = models.IntegerField(null=True, blank=True)
    over_gg_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_hero_play_time(self):
        used_heroes = Counter()
        q = self.heropick_set.filter(~Q(new_hero__name='n/a')).all()
        for h in q:
            end = h.end_time_point
            if end is None:
                end = h.round.duration
            used_heroes[h.new_hero.name] += end - h.time_point
        return used_heroes

    def get_position(self):
        hero_types = Counter()
        q = self.heropick_set.filter(~Q(new_hero__name='n/a')).all()
        for h in q:
            end = h.end_time_point
            if end is None:
                end = h.round.duration
            hero_types[h.new_hero.get_type_display()] += end - h.time_point
        if not hero_types:
            return ''
        return max(hero_types.keys(), key=lambda x: hero_types[x])

    def generate_stats(self, all_stats=False):
        stat_types = ['final_blows', 'assists', 'deaths', 'ults_gained', 'ults_used']
        #stat_types += [x + '_per10' for x in stat_types]
        stats = {x: 0 for x in stat_types}
        hero_specific_stats = {}
        hero_play_time = self.get_hero_play_time()
        total_time = sum(hero_play_time.values())
        total_time_per_ten = total_time / 600

        ultimates = Ultimate.objects.filter(player=self)
        stats['ults_gained'] = ultimates.count() / total_time_per_ten
        stats['ults_used'] = ultimates.filter(used__isnull=False).count() / total_time_per_ten
        stats['final_blows'] = self.kills.filter(ability__type=Ability.DAMAGING_TYPE).count() / total_time_per_ten
        stats['assists'] = self.assist_set.count() / total_time_per_ten
        stats['deaths'] = self.deaths.filter(ability__type=Ability.DAMAGING_TYPE,
                                            dying_npc__isnull=True, denied_ult__isnull=True).count() / total_time_per_ten

        d = {'stats': stats, 'hero_play_time': hero_play_time}
        return d

    def get_latest_matches(self):
        m = Match.objects.filter(Q(game__left_team__playerparticipation__player=self) |
                                        Q(game__right_team__playerparticipation__player=self)).order_by('-date').distinct()[:5]
        return m

    def get_hero_at_timepoint(self, round_object, time_point):
        time_point = round(time_point, 1)
        s = self.heropick_set.filter(time_point__lte=time_point, round=round_object).order_by(
            '-time_point').prefetch_related('new_hero', 'new_hero__abilities').first()
        if s is not None:
            return s.new_hero
        return ''

    def get_ult_states(self, round_object):
        ultimates = self.ultimate_set.filter(round=round_object).all()
        round_end = round(round_object.end - round_object.begin, 1)
        if len(ultimates) == 0:
            return [{'begin': 0, 'end': round_end, 'status': 'no_ult'}]

        switches = self.heropick_set.filter(round=round_object).all()
        switch_time_points = [round(x.time_point, 1) for x in switches]
        segments = []
        for u in ultimates:
            if segments:
                segments.append({'begin': segments[-1]['end'], 'end': u.gained, 'status': 'no_ult'})
            else:
                segments.append({'begin': 0, 'end': u.gained, 'status': 'no_ult'})
            if u.used:
                segments.append({'begin': u.gained, 'end': u.used, 'status': 'has_ult', 'id':u.id})
                if u.ended:
                    segments.append({'begin': u.used, 'end': u.ended, 'status': 'using_ult', 'id':u.id})
            else:
                for stp in switch_time_points:
                    if stp < u.gained:
                        continue
                    segments.append({'begin': u.gained, 'end': stp, 'status': 'has_ult', 'id':u.id})
                    break
                else:
                    segments.append({'begin': u.gained, 'end': round_end, 'status': 'has_ult', 'id':u.id})
        if segments[-1]['end'] < round_end:
            segments.append({'begin': segments[-1]['end'], 'end': round_end, 'status': 'no_ult'})
        return segments

    def get_alive_states(self, round_object):
        from django.db.models import Q
        deaths = self.deaths.filter(round=round_object, dying_npc=None)
        deaths = deaths.filter(Q(ability__isnull=True) | Q(ability__type=Ability.DAMAGING_TYPE)).all()
        round_end = round_object.end - round_object.begin
        if len(deaths) == 0:
            return [{'begin': 0, 'end': round_end, 'status': 'alive'}]
        revives = self.deaths.filter(round=round_object, ability__type=Ability.REVIVING_TYPE).all()
        segments = []
        for d in deaths:
            actual_death = d.time_point - Decimal('0.2')
            respawn_time = actual_death + Decimal('10.0')
            if round_object.is_overtime(actual_death):
                respawn_time += Decimal('3.0')

            if segments:
                segments.append({'begin': segments[-1]['end'], 'end': actual_death, 'status': 'alive'})
            else:
                segments.append({'begin': Decimal('0.0'), 'end': actual_death, 'status': 'alive'})
            for r in revives:
                actual_revive = r.time_point - Decimal('0.2')
                if 0 < actual_revive < respawn_time and actual_revive > actual_death:
                    segments.append({'begin': actual_death, 'end': actual_revive, 'status': 'dead'})
                    break
            else:
                segments.append({'begin': actual_death, 'end': respawn_time, 'status': 'dead'})
        if segments[-1]['end'] < round_end:
            segments.append({'begin': segments[-1]['end'], 'end': round_end, 'status': 'alive'})

        return segments

    def get_status_effect_states(self, round_object):
        status_effects = self.statuseffect_set.filter(round=round_object, status__independent=False).all()
        round_end = round_object.end - round_object.begin
        if len(status_effects) == 0:
            segments = [{'begin': 0, 'end': round_end, 'status': 'normal'}]
        else:
            segments = []
            for s in status_effects:
                status_name = s.status.name.lower()
                if segments:
                    segments.append({'begin': segments[-1]['end'], 'end': s.start_time, 'status': 'normal'})
                else:
                    segments.append({'begin': Decimal('0.0'), 'end':  s.start_time, 'status': 'normal'})
                segments.append({'begin': s.start_time, 'end': s.end_time, 'status': status_name})
            if segments[-1]['end'] < round_end:
                segments.append({'begin': segments[-1]['end'], 'end': round_end, 'status': 'normal'})
        effects = {'status':segments}
        status = Status.objects.filter(independent=True).all()
        for stat in status:
            status_name = stat.name.lower()
            status_effects = self.statuseffect_set.filter(round=round_object, status=stat).all()
            if len(status_effects) == 0:
                segments = [{'begin': 0, 'end': round_end, 'status': 'not_'+ status_name}]
            else:
                segments = []
                for s in status_effects:
                    if segments:
                        segments.append({'begin': segments[-1]['end'], 'end': s.start_time, 'status': 'not_'+ status_name})
                    else:
                        segments.append({'begin': Decimal('0.0'), 'end':  s.start_time, 'status': 'not_'+ status_name})
                    segments.append({'begin': s.start_time, 'end': s.end_time, 'status': status_name})
                if segments[-1]['end'] < round_end:
                    segments.append({'begin': segments[-1]['end'], 'end': round_end, 'status': 'not_'+ status_name})
            effects[status_name] = segments
        return effects

    def get_hero_states(self, round_object):
        switches = self.heropick_set.filter(round=round_object).all()
        round_end = round_object.end - round_object.begin
        if len(switches) == 1:
            return [{'begin': 0, 'end': round_end, 'hero': switches[0].new_hero}]
        segments = []
        for i, s in enumerate(switches):
            if i != len(switches) - 1:
                segments.append({'begin': s.time_point, 'end': switches[i + 1].time_point, 'hero': s.new_hero})
            else:
                segments.append({'begin': segments[-1]['end'], 'end': round_end, 'hero': s.new_hero})
        return segments

    class Meta:
        ordering = ['name']


class PlayerName(models.Model):
    name = models.CharField(max_length=128)


class PlayerNameUse(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    name = models.ForeignKey(PlayerName, on_delete=models.CASCADE)


class Team(models.Model):
    name = models.CharField(max_length=128)
    players = models.ManyToManyField(Player, through='Affiliation')
    home_color = RGBColorField(default='#54fefd')
    away_color = RGBColorField(default='#ff122c')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Affiliation(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)


class Event(models.Model):
    ORIGINAL = 'O'
    WORLD_CUP = 'W'
    OWL = 'L'
    CONTENDERS = 'C'
    SPECTATOR_MODE_CHOICES = ((ORIGINAL, 'Original'),
                              (WORLD_CUP, 'World Cup'),
                              (OWL, 'Overwatch League'),
                              (CONTENDERS, 'Contenders'),)
    name = models.CharField(max_length=128)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    liquipedia_id = models.CharField(max_length=128, null=True, blank=True)
    spectator_mode = models.CharField(max_length=1, choices=SPECTATOR_MODE_CHOICES, default='S')
    film_format = models.CharField(max_length=1, choices=FILM_FORMAT_CHOICES, default=ORIGINAL)
    stream_channels = models.ManyToManyField(StreamChannel, related_name='events')
    teams = models.ManyToManyField(Team, through='EventParticipation')
    channel_query_string = models.CharField(max_length=128, null=True, blank=True)
    default_patch = models.ForeignKey(Patch, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.name


class EventParticipation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    result = models.CharField(max_length=128, null=True, blank=True)


class Match(models.Model):
    COMP = 'C'
    RULES_CHOICES = (
        (COMP, 'Competitive'),
        ('M', 'Mystery heroes')
                     )
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Team)
    description = models.CharField(max_length=256)
    date = models.DateField(blank=True, null=True)
    rules = models.CharField(max_length=1, choices=RULES_CHOICES, default=COMP)
    exhibition = models.BooleanField(default=False)
    patch = models.ForeignKey(Patch, on_delete=models.SET_NULL, null=True, blank=True)
    owl_id = models.IntegerField(null=True, blank=True)
    over_gg_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return 'Match between {} in {}'.format(' and '.join(x.name for x in self.teams.all()), str(self.event))

    class Meta:
        ordering = ['-id']
        verbose_name_plural = "matches"

    @property
    def team_description(self):
        return ' and '.join(x.name for x in self.teams.all())

    @property
    def start_time(self):
        first_game = self.game_set.first()
        if first_game is not None:
            first_round = first_game.round_set.first()
            if first_round is not None:
                return first_round.begin
        return 0

    def generate_stats(self, all_stats=False):
        data = {'maps': []}
        if self.date is None:
            self.date = self.game_set.first().round_set.first().stream_vod.broadcast_date.date()
            self.save()

        data['date'] = self.date
        for g in self.game_set.prefetch_related('left_team__team', 'right_team__team', 'map').all():
            if 'team_one' not in data:
                data['team_one'] = g.left_team.team.name
                data['team_two'] = g.right_team.team.name
            map_data = {'map': g.map.name,
                        'game_number': g.game_number
                        }
            d = g.generate_stats(all_stats=all_stats)
            map_data.update(d)
            data['maps'].append(map_data)
        return data


class Game(models.Model):
    game_number = models.IntegerField()
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    left_team = models.OneToOneField('TeamParticipation', on_delete=models.CASCADE, related_name='left_team')
    right_team = models.OneToOneField('TeamParticipation', on_delete=models.CASCADE, related_name='right_team')
    map = models.ForeignKey(Map, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("match", "game_number"),)
        ordering = ['-match__id', 'game_number']

    def generate_stats(self, all_stats=False):
        stat_types = ['final_blows', 'assists', 'deaths', 'ults_gained', 'ults_used']
        #stat_types += [x + '_per10' for x in stat_types]
        left_team_name = self.left_team.team.name
        right_team_name = self.right_team.team.name
        stats = {left_team_name: {}, right_team_name: {}}
        hero_stats = {left_team_name: {}, right_team_name: {}}
        left_team_players = self.left_team.players.all()
        right_team_players = self.right_team.players.all()
        for r in self.round_set.prefetch_related('ultimate_set', 'killfeedevent_set__ability').all():
            for i, p in enumerate(list(left_team_players) + list(right_team_players)):
                if i < 6:
                    side = left_team_name
                else:
                    side = right_team_name
                if p.name not in stats[side]:
                    stats[side][p.name] = {x: 0 for x in stat_types}
                    hero_stats[side][p.name] = {}
            for i, p in enumerate(list(left_team_players) + list(right_team_players)):
                if i < 6:
                    side = left_team_name
                    friendly_team = left_team_players
                    enemy_team = right_team_players
                else:
                    side = right_team_name
                    friendly_team = right_team_players
                    enemy_team = left_team_players

                hero_picks = p.get_hero_states(r)
                for hp in hero_picks:
                    hero_name = hp['hero'].name
                    if hero_name not in hero_stats[side][p.name]:
                        hero_stats[side][p.name][hero_name] = Counter()
                    hero_stats[side][p.name][hero_name]['play_time'] += hp['end'] - hp['begin']

                    ultimates = r.ultimate_set.filter(player=p, gained__lte=hp['end'], gained__gte=hp['begin'])
                    hero_stats[side][p.name][hero_name]['ults_gained'] += len(ultimates)
                    hero_stats[side][p.name][hero_name]['ults_used'] += len([x for x in ultimates if x.used is not None])
                    stats[side][p.name]['ults_gained'] += len(ultimates)
                    stats[side][p.name]['ults_used'] += len([x for x in ultimates if x.used is not None])

                    kills = r.killfeedevent_set.filter(killing_player=p, time_point__lte=hp['end'],
                                                       time_point__gte=hp['begin'], ability__type=Ability.DAMAGING_TYPE)
                    hero_stats[side][p.name][hero_name]['final_blows'] += len(kills)
                    stats[side][p.name]['final_blows'] += len(kills)

                    assists = p.assist_set.filter(kill__round=r, kill__time_point__lte=hp['end'],
                                                  kill__time_point__gte=hp['begin'])
                    hero_stats[side][p.name][hero_name]['assists'] += len(assists)
                    stats[side][p.name]['assists'] += len(assists)
                    deaths = r.killfeedevent_set.filter(dying_player=p, time_point__lte=hp['end'],
                                                        time_point__gte=hp['begin'], ability__type=Ability.DAMAGING_TYPE,
                                                        dying_npc__isnull=True, denied_ult__isnull=True)
                    hero_stats[side][p.name][hero_name]['deaths'] += len(deaths)
                    stats[side][p.name]['deaths'] += len(deaths)

                    if all_stats:
                        if hero_name.lower() in ['d.va', 'sigma']:
                            ults_denied = r.killfeedevent_set.filter(killing_player=p, ability__type=Ability.DENYING_TYPE,
                                                                     denied_ult__isnull=False, time_point__gte=hp['begin'],
                                                                     time_point__lte=hp['end'])
                            hero_stats[side][p.name][hp['hero'].name]['ults_denied'] += len(ults_denied)
                        if hero_name.lower() == 'd.va':
                            mech_deaths = r.killfeedevent_set.filter(dying_player=p, ability__type=Ability.DAMAGING_TYPE,
                                                                     dying_npc__isnull=False, denied_ult__isnull=True,
                                                                     time_point__gte=hp['begin'],
                                                                     time_point__lte=hp['end'])
                            hero_stats[side][p.name][hero_name]['mech_deaths'] += len(mech_deaths)
                        elif hero_name.lower() == 'orisa':
                            supercharger_deaths = r.killfeedevent_set.filter(dying_player=p,
                                                                             ability__type=Ability.DAMAGING_TYPE,
                                                                             dying_npc__isnull=False, denied_ult__isnull=True,
                                                                     time_point__gte=hp['begin'],
                                                                     time_point__lte=hp['end'])
                            hero_stats[side][p.name][hero_name]['supercharger_deaths'] += len(supercharger_deaths)
                            #ultimates = r.ultimate_set.filter(player=p, used__isnull=False)
                            #average_ultimate_duration = sum(x.end_time - x.start_time for x in ultimates) / len(ultimates)
                            #hero_specific_stats[side][p.name][hero_name]['average_supercharger_life'] += len(supercharger_deaths)
                        elif hero_name.lower() == 'ana':
                            num_antis = r.statuseffect_set.filter(status__causing_hero=hp['hero'], player__in=enemy_team,
                                                                  status__name='Antiheal', start_time__gte=hp['begin'],
                                                                  start_time__lte=hp['end'])
                            hero_stats[side][p.name][hero_name]['number_of_antiheals'] += len(
                                num_antis)
                            num_sleeps = r.statuseffect_set.filter(status__causing_hero=hp['hero'], player__in=enemy_team,
                                                                   status__name='Asleep', start_time__gte=hp['begin'],
                                                                  start_time__lte=hp['end'])
                            hero_stats[side][p.name][hero_name]['number_of_sleeps'] += len(
                                num_sleeps)
                        elif hero_name.lower() == 'mercy':
                            revives = r.killfeedevent_set.filter(killing_player=p, ability__type=Ability.REVIVING_TYPE)
                            hero_stats[side][p.name][hero_name]['revives'] += len(revives)
                        elif hero_name.lower() == 'sombra':
                            hacks = r.statuseffect_set.filter(status__causing_hero=hp['hero'], player__in=enemy_team,
                                                                  status__name='Hacked', start_time__gte=hp['begin'],
                                                                  start_time__lte=hp['end'])
                            hero_stats[side][p.name][hero_name]['number_of_hacks'] += len(hacks)
                            hero_stats[side][p.name][hero_name]['hacked_duration'] += sum([x.end_time - x.start_time for x in hacks])
                        elif hero_name.lower() == 'baptiste':
                            immortality_deaths = r.killfeedevent_set.filter(dying_player=p,
                                                                             ability__type=Ability.DAMAGING_TYPE,
                                                                             dying_npc__isnull=False, denied_ult__isnull=True,
                                                                     time_point__gte=hp['begin'],
                                                                     time_point__lte=hp['end'])
                            hero_stats[side][p.name][hero_name]['immortality_field_deaths'] += len(immortality_deaths)
                            immortals = r.statuseffect_set.filter(status__causing_hero=hp['hero'], player__in=friendly_team,
                                                                  status__name='Immortal', start_time__gte=hp['begin'],
                                                                  start_time__lte=hp['end'])
                            hero_stats[side][p.name][hero_name]['immortality_time'] += sum([x.end_time - x.start_time for x in immortals])
                        elif hero_name.lower() == 'mei':
                            frozen = r.statuseffect_set.filter(status__causing_hero=hp['hero'], player__in=enemy_team,
                                                                  status__name='Frozen', start_time__gte=hp['begin'],
                                                                  start_time__lte=hp['end'])
                            hero_stats[side][p.name][hero_name]['enemies_frozen'] += len(
                                frozen)
                            hero_stats[side][p.name][hero_name]['frozen_duration'] += sum([x.end_time - x.start_time for x in frozen])
                        elif hero_name.lower() == 'lúcio':
                            beats_cancelled = r.ultimate_set.filter(player=p, used__isnull=False, ended__lt=r.end-Decimal('0.1'))
                            beats_cancelled = [x for x in beats_cancelled if x.ended - x.used < 3]
                            hero_stats[side][p.name][hero_name]['beats_lost'] += len(beats_cancelled)
                        if hero_name.lower() in ['widowmaker', 'mccree']:
                            headshot_kills = r.killfeedevent_set.filter(killing_player=p, ability__type=Ability.DAMAGING_TYPE, headshot=True)
                            hero_stats[side][p.name][hero_name]['headshot_final_blows'] += len(headshot_kills)
                        if hp['hero'].abilities.filter(deniable=True).count() > 0:
                            ults_eaten = r.killfeedevent_set.filter(dying_player=p,
                                                                             ability__type=Ability.DENYING_TYPE,
                                                                             dying_npc__isnull=True, denied_ult__isnull=False,
                                                                     time_point__gte=hp['begin'],
                                                                     time_point__lte=hp['end'])
                            hero_stats[side][p.name][hero_name]['ults_denied_by_enemy'] += len(ults_eaten)
                        try:
                            ultimate = hp['hero'].abilities.get(ultimate=True, type=Ability.DAMAGING_TYPE)
                            ultimate_kills = r.killfeedevent_set.filter(killing_player=p, ability=ultimate)
                            hero_stats[side][p.name][hero_name]['ultimate_final_blows'] = len(ultimate_kills)
                        except Ability.DoesNotExist:
                            pass
        d = {'stats': stats, 'hero_stats': hero_stats}
        return d


class TeamParticipation(models.Model):
    BLUE = 'B'
    COLOR_CHOICES = (
        (BLUE, 'Blue'),
        ('R', 'Red'),
        ('W', 'White'),
        ('G', 'Green'),
        ('O', 'Orange'),
        ('Y', 'Yellow'),
        ('P', 'Purple'),
        ('I', 'Pink'),
        ('K', 'Black'),
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    use_home_color = models.BooleanField(default=False)
    color = models.CharField(max_length=1, choices=COLOR_CHOICES, default=BLUE)
    points = models.IntegerField(null=True, blank=True)
    subpoints = models.CharField(max_length=128, null=True, blank=True)
    players = models.ManyToManyField(Player, through='PlayerParticipation')

    def get_color_hex(self, spectator_mode):
        if spectator_mode == Event.CONTENDERS:
            if self.color == 'W':
                return settings.CONTENDERS_AWAY_COLOR
            return settings.CONTENDERS_HOME_COLOR
        elif spectator_mode in [Event.OWL, Event.WORLD_CUP]:
            if self.color == 'W':
                return self.team.away_color
            return self.team.home_color
        return settings.COLOR_MAPPING[self.get_color_display().lower()]

    @classmethod
    def get_color_code(cls, display_color):
        for code, color in cls.COLOR_CHOICES:
            if display_color.lower() == color.lower():
                return code
        return cls.BLUE

    class Meta:
        ordering = ['points', 'subpoints']


class PlayerParticipation(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team_participation = models.ForeignKey(TeamParticipation, on_delete=models.CASCADE)
    player_index = models.IntegerField()

    class Meta:
        ordering = ['player_index']
        unique_together = (("team_participation", "player_index"),)


class Round(models.Model):
    ANNOTATION_CHOICES = (('N', 'None'),
                          ('W', "Winston's lab"),
                          ('M', 'Manual'),
                          ('O', 'Omnic intelligence'))
    stream_vod = models.ForeignKey(StreamVod, on_delete=models.SET_NULL, null=True, blank=True)
    round_number = models.IntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    attacking_side = models.CharField(max_length=1, choices=SIDE_CHOICES, default=NEITHER)
    submap = models.ForeignKey(Submap, null=True, blank=True, on_delete=models.SET_NULL)
    begin = models.DecimalField(max_digits=6, decimal_places=1, default=Decimal('0.0'))
    end = models.DecimalField(max_digits=6, decimal_places=1, default=Decimal('0.0'))
    annotation_status = models.CharField(max_length=1, choices=ANNOTATION_CHOICES, default='N')
    exclude_for_training = models.BooleanField(default=False)

    class Meta:
        unique_together = (("game", "round_number"),)
        ordering = ['game__match__id', 'game__game_number', 'round_number']

    def __str__(self):
        return 'Round {} of Game {} for {} vs {} in {}'.format(self.round_number, self.game.game_number,
                                                               self.game.left_team.team, self.game.right_team.team,
                                                               self.game.match.event)

    def reset(self):
        self.annotation_status = 'N'
        self.heropick_set.all().delete()
        self.killfeedevent_set.all().delete()
        self.ultimate_set.all().delete()
        self.statuseffect_set.all().delete()
        self.pointflip_set.all().delete()
        self.pointgain_set.all().delete()
        self.overtime_set.all().delete()
        self.save()

    @property
    def duration(self):
        return self.end - self.begin

    def fix_switch_end_points(self):
        switches = self.heropick_set.order_by('-time_point').prefetch_related('player').all()
        last_switches = {}
        for s in switches:
            if s.player.id not in last_switches:
                if s.end_time_point != self.duration:
                    s.end_time_point = self.duration
                    s.save()
            else:
                if s.end_time_point != last_switches[s.player.id]:
                    s.end_time_point = last_switches[s.player.id]
                    s.save()
            last_switches[s.player.id] = s.time_point

    def get_player_of_hero(self, hero_name, time_point, side):
        if side == 'left':
            player_set = self.game.left_team.playerparticipation_set.all()
        else:
            player_set = self.game.right_team.playerparticipation_set.all()
        for p in player_set:
            hero = p.player.get_hero_at_timepoint(self, time_point)
            if not hero:
                continue
            if hero.name.lower() == hero_name.lower():
                return p.player

    def has_hero(self, hero, time_point, side):
        q = HeroPick.objects.filter(round=self, time_point__lte=time_point,
                                    end_time_point__gt=time_point)
        if side == 'left':
            q = q.filter(player__in=self.game.left_team.players.all())
        else:
            q = q.filter(player__in=self.game.right_team.players.all())
        if isinstance(hero, Hero):
            q = q.filter(new_hero=hero)
        else:
            q = q.filter(new_hero__in=hero)
        return bool(len(q))

    def has_many_empty_deaths(self):
        relative_threshold = 0.3
        empty_death_count = self.killfeedevent_set.filter(killing_player__isnull=True).count()
        all_kills = self.killfeedevent_set.count()
        if all_kills == 0:
            return False
        if empty_death_count / all_kills > relative_threshold:
            return True
        return False

    def has_overlapping_heroes(self):
        teams = [self.game.left_team.playerparticipation_set.all(), self.game.right_team.playerparticipation_set.all()]
        for t in teams:
            hero_states = {}
            for p in t:
                pp = p.player
                hero_states[pp.name] = pp.get_hero_states(self)

            for i, (k, v) in enumerate(hero_states.items()):
                to_check = list(hero_states.items())[i+1:]
                for k2, v2 in to_check:
                    for interval_one in v:
                        for interval_two in v2:
                            if interval_two['begin'] <= interval_one['begin'] <= interval_two['end'] \
                                    and interval_one['hero'] == interval_two['hero']:
                                print('FOUND')
                                print(self.id)
                                print(k, k2)
                                print(interval_one)
                                print(interval_two)
                                return True

        return False

    def get_player_states(self):
        data = {'left': {}, 'right': {}}
        left_team = self.game.left_team.playerparticipation_set.all()
        right_team = self.game.right_team.playerparticipation_set.all()
        for p in left_team:
            pp = p.player
            hero_states = pp.get_hero_states(self)

            data['left'][p.player_index] = {'ult': pp.get_ult_states(self), 'alive': pp.get_alive_states(self),
                                            'hero': hero_states, 'player': pp.name}
            data['left'][p.player_index].update(pp.get_status_effect_states(self))
        for p in right_team:
            pp = p.player
            hero_states = pp.get_hero_states(self)
            data['right'][p.player_index] = {'ult': pp.get_ult_states(self), 'alive': pp.get_alive_states(self),
                                             'hero': hero_states, 'player': pp.name}
            data['right'][p.player_index].update(pp.get_status_effect_states(self))
        return data

    def get_status_duration(self):
        status_durations = {}
        q = self.statuseffect_set.prefetch_related('status').all()
        for s in q:
            status = s.status.name
            if status not in status_durations:
                status_durations[status] = 0
            status_durations[status] += s.end_time - s.start_time
        return status_durations

    def get_hero_play_time(self):
        from django.db.models import Q
        used_heroes = Counter()
        q = self.heropick_set.filter(~Q(new_hero__name='n/a')).all()
        for h in q:
            if self.pk == 7015:
                print(h, h.player.name, h.time_point, h.end_time_point)
            end = h.end_time_point
            if end is None:
                end = self.duration
            used_heroes[h.new_hero.name] += end - h.time_point
        return used_heroes

    def get_heroes_used(self):
        used_heroes = self.get_hero_play_time()
        return sorted(used_heroes.keys(), key=lambda x: -used_heroes[x])

    @property
    def replay_duration(self):
        replays = self.replay_set.all()

        round_end = self.end - self.begin
        return sum(x.end_time - x.start_time if x.end_time is not None else round_end - x.start_time for x in replays)

    @property
    def pause_duration(self):
        pauses = self.pause_set.all()

        round_end = self.end - self.begin
        return sum(x.end_time - x.start_time if x.end_time is not None else round_end - x.start_time for x in pauses)

    @property
    def sequences(self):
        replays = self.replay_set.all()
        pauses = self.pause_set.all()
        smaller_windows = self.smallerwindow_set.all()
        if len(replays) == 0 and len(pauses) == 0 and len(smaller_windows) == 0:
            return [[0, self.end - self.begin]]
        interruptions = sorted([x for x in replays] + [x for x in pauses] + [x for x in smaller_windows],
                               key=lambda x: x.start_time)

        round_end = Decimal(self.end - self.begin)
        cur_beg = Decimal('0.00')
        segments = []
        for i, s in enumerate(interruptions):
            segments.append([cur_beg, s.start_time - Decimal('0.1')])
            if s.end_time is not None:
                cur_beg = s.end_time
            else:
                cur_beg = round_end
        if round_end - cur_beg > 1:
            segments.append([cur_beg, round_end])

        return segments

    def get_side_and_index(self, player):
        if player in self.game.left_team.players.all():
            ind = self.game.left_team.playerparticipation_set.filter(player=player).get().player_index
            return 'L', ind
        ind = self.game.right_team.playerparticipation_set.filter(player=player).get().player_index
        return 'R', ind

    def get_round_states(self, identifier):
        if identifier == 'smaller_window':
            events = self.smallerwindow_set.all()
        elif identifier == 'replay':
            events = self.replay_set.all()
        elif identifier == 'pause':
            events = self.pause_set.all()
        elif identifier == 'overtime':
            events = self.overtime_set.all()
        else:
            raise Exception('{} not a round state.'.format(identifier))
        round_end = self.end - self.begin
        if len(events) == 0:
            return [{'begin': 0, 'end': round_end, 'status': 'not_' + identifier}]
        states = []
        prev = 0
        for o in events:
            states.append({'begin': prev, 'end': o.start_time, 'status': 'not_'+ identifier})
            states.append({'begin': o.start_time, 'end': o.end_time, 'status': identifier})
            prev = o.end_time
        if states[-1]['end'] is None:
            states[-1]['end'] = round_end
        elif states[-1]['end'] != round_end:
            states.append({'begin': states[-1]['end'], 'end': round_end, 'status': 'not_'+ identifier})
        return states

    def get_zoomed_bars_states(self):
        replays = self.zoom_set.all()
        round_end = self.end - self.begin
        identifier = 'zoomed'
        default = [{'begin': 0, 'end': round_end, 'status': 'not_' + identifier}]
        if len(replays) == 0:
            return {'left':default,
                    'right':default}
        states = {'left':[],
                 'right':[]}
        prev = {'left': 0, 'right': 0}
        for o in replays:
            if o.side == 'L':
                s = 'left'
            else:
                s = 'right'
            states[s].append({'begin': prev[s], 'end': o.start_time, 'status': 'not_'+ identifier})
            states[s].append({'begin': o.start_time, 'end': o.end_time, 'status': identifier})
            prev[s] = o.end_time
        for s in ['left', 'right']:
            if not states[s]:
                states[s] = default
            else:
                if states[s][-1]['end'] is None:
                    states[s][-1]['end'] = round_end
                elif states[s][-1]['end'] != round_end:
                    states[s].append({'begin': states[s][-1]['end'], 'end': round_end, 'status': 'not_'+ identifier})
        return states

    def get_point_status_states(self):
        map_type = self.game.map.get_mode_display()
        states = []
        round_end = self.end - self.begin
        if map_type == 'Control':
            flips = self.pointflip_set.all()
            for i, f in enumerate(flips):
                if not states:
                    states.append({'begin': 0, 'end': f.time_point, 'status': 'Control_neither'})

                if i != len(flips) - 1:
                    end_point = flips[i + 1].time_point
                else:
                    end_point = round_end
                side = 'Control_left'
                if f.controlling_side == 'R':
                    side = 'Control_right'
                states.append({'begin': f.time_point, 'end': end_point, 'status': side})
        else:
            point_gains = self.pointgain_set.all()
            if not point_gains:
                if map_type in ['Assault']:
                    return [{'begin': 0, 'end': round_end, 'status': 'Assault_1'}]
                else:
                    return [{'begin': 0, 'end': round_end, 'status': '{}_1'.format(map_type)}]
            for i, p in enumerate(point_gains):
                if map_type == 'Assault':
                    if not states:
                        states.append({'begin': 0, 'end': p.time_point, 'status': 'Assault_1'})
                    if p.point_total % 2 != 0:
                        states.append({'begin': p.time_point, 'end': round_end, 'status': 'Assault_2'})
                else:
                    if not states:
                        states.append({'begin': 0, 'end': p.time_point, 'status': '{}_1'.format(map_type)})
                    if i != len(point_gains) - 1:
                        end_point = point_gains[i + 1].time_point
                    else:
                        end_point = round_end
                    if p.point_total % 3 == 1:
                        states.append({'begin': p.time_point, 'end': end_point, 'status': '{}_2'.format(map_type)})
                    elif p.point_total % 3 == 2:
                        states.append({'begin': p.time_point, 'end': end_point, 'status': '{}_3'.format(map_type)})
        return states

    def point_status(self, time_point):
        map_type = self.game.map.get_mode_display()
        if map_type == 'Control':
            last_flip = self.pointflip_set.filter(time_point__lte=time_point).order_by(
                '-time_point').first()
            if last_flip is None:
                return 'control_none'
            if last_flip.controlling_side == 'L':
                return 'control_left'
            return 'control_right'
        else:
            last_points = self.pointgain_set.filter(time_point__lte=time_point).order_by(
                '-time_point').first()
            if map_type == 'Assault':
                if last_points is None or last_points.point_total % 2 == 0:
                    return 'Assault_A'
                else:
                    return 'Assault_B'

            if last_points is None or last_points.point_total % 3 == 0:
                if map_type == 'Hybrid':
                    return 'Assault_A'
                elif map_type == 'Escort':
                    return 'Escort_1'
            elif last_points.point_total % 3 == 1:
                return 'Escort_2'
            else:
                return 'Escort_3'

    def is_replay(self, time_point):
        if self.replay_set.filter(start_time__lte=time_point, end_time__gte=time_point).count() != 0:
            return True

    def is_paused(self, time_point):
        if self.pause_set.filter(start_time__lte=time_point, end_time__gte=time_point).count() != 0:
            return True
        return False

    def is_overtime(self, time_point):
        if self.overtime_set.filter(start_time__lte=time_point, end_time__gte=time_point).count() != 0:
            return True
        return False

    def get_kill_feed_events(self):
        potential_killfeed = []
        items = self.killfeedevent_set.prefetch_related('killing_player', 'dying_player', 'ability').all()
        for event in items:
            killing_hero = 'N/A'
            killing_color = 'N/A'
            killing_color_hex = 'N/A'
            killing_player = 'N/A'
            killing_side = 'neither'
            if event.killing_player is not None:
                killing_hero = event.killing_player.get_hero_at_timepoint(self, event.time_point).name
                killing_player = event.killing_player.name
                if self.game.left_team.playerparticipation_set.filter(player=event.killing_player).count():
                    killing_team = self.game.left_team
                    killing_side = 'left'
                else:
                    killing_team = self.game.right_team
                    killing_side = 'right'

                killing_color = killing_team.get_color_display().lower()
                killing_color_hex = killing_team.get_color_hex(self.game.match.event.spectator_mode)
            if self.game.left_team.playerparticipation_set.filter(player=event.dying_player).count():
                dying_team = self.game.left_team
                dying_side = 'left'
            else:
                dying_team = self.game.right_team
                dying_side = 'right'
            dying_color = dying_team.get_color_display()
            dying_color_hex = dying_team.get_color_hex(self.game.match.event.spectator_mode)

            assists = Assist.objects.filter(kill=event)
            assisting_heroes = []
            for a in assists:
                assisting_heroes.append(a.player.get_hero_at_timepoint(self, event.time_point).name)
            if event.denied_ult is not None:
                dying_hero = event.denied_ult.name
            elif event.dying_npc is not None:
                dying_hero = event.dying_npc.name
            else:
                dying_hero = event.dying_player.get_hero_at_timepoint(self, event.time_point).name
            ability_name = 'N/A'
            if event.ability is not None:
                ability_name = event.ability.name
            potential_killfeed.append(
                {'time_point': event.time_point, 'first_hero': killing_hero, 'first_player': killing_player,
                 'first_color': killing_color, 'first_color_hex': killing_color_hex,
                 'first_side': killing_side,
                 'assisting_heroes': assisting_heroes,
                 'ability': ability_name, 'headshot': event.headshot,
                 'second_hero': dying_hero, 'second_player': event.dying_player.name,
            'second_color': dying_color, 'second_color_hex': dying_color_hex, 'second_side': dying_side})

        potential_killfeed = sorted(potential_killfeed, key=lambda x: x['time_point'])
        return potential_killfeed


class Pause(models.Model):
    start_time = models.DecimalField(max_digits=6, decimal_places=1, default=Decimal('0.0'))
    end_time = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "start_time"),)
        ordering = ['round', 'start_time']


class Replay(models.Model):
    start_time = models.DecimalField(max_digits=6, decimal_places=1, default=Decimal('0.0'))
    end_time = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "start_time"),)
        ordering = ['round', 'start_time']


class SmallerWindow(models.Model):
    start_time = models.DecimalField(max_digits=6, decimal_places=1, default=Decimal('0.0'))
    end_time = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "start_time"),)
        ordering = ['round', 'start_time']


class Zoom(models.Model):
    start_time = models.DecimalField(max_digits=6, decimal_places=1, default=Decimal('0.0'))
    end_time = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    side = models.CharField(max_length=1, choices=SIDE_CHOICES, default=NEITHER)

    class Meta:
        unique_together = (("round", "start_time", "side"),)
        ordering = ['round', 'start_time', "side"]


class Overtime(models.Model):
    start_time = models.DecimalField(max_digits=6, decimal_places=1, default=Decimal('0.0'))
    end_time = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "start_time"),)
        ordering = ['round', 'start_time']


class StatusEffect(models.Model):
    start_time = models.DecimalField(max_digits=6, decimal_places=1)
    end_time = models.DecimalField(max_digits=6, decimal_places=1)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "start_time", 'player', 'status'),)
        ordering = ['round', 'start_time', 'player']


class PointGain(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    time_point = models.DecimalField(max_digits=6, decimal_places=1)
    point_total = models.IntegerField()

    class Meta:
        unique_together = (("round", "time_point"),)
        ordering = ['round', 'time_point']

    def __str__(self):
        return 'Point gain to {} at {}'.format(self.point_total, self.time_point)


class PointFlip(models.Model):
    time_point = models.DecimalField(max_digits=6, decimal_places=1)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    controlling_side = models.CharField(max_length=1, choices=SIDE_CHOICES, default=NEITHER)

    class Meta:
        unique_together = (("round", "time_point"),)
        ordering = ['round', 'time_point']


class Assist(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    kill = models.ForeignKey('KillFeedEvent', on_delete=models.CASCADE)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return '{} - {}'.format(self.order, self.player.name)


class KillFeedEvent(models.Model):
    time_point = models.DecimalField(max_digits=6, decimal_places=1)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    killing_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='kills', blank=True, null=True)
    assists = models.ManyToManyField(Player, through=Assist)
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE, blank=True, null=True)
    headshot = models.BooleanField(default=False)
    dying_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='deaths')
    dying_npc = models.ForeignKey(NPC, on_delete=models.CASCADE, blank=True, null=True)
    denied_ult = models.ForeignKey(Ability, on_delete=models.CASCADE, related_name='denials', blank=True, null=True)

    class Meta:
        unique_together = (("round", "time_point", "killing_player", "dying_player", 'dying_npc', 'denied_ult'),)
        ordering = ['round', 'time_point', 'killing_player', 'dying_player']

    def __str__(self):
        dying_entity = str(self.dying_player)
        if self.dying_npc is not None:
            dying_entity += ' ({})'.format(self.dying_npc)
        if self.denied_ult is not None:
            dying_entity += ' ({})'.format(self.denied_ult)
        if self.ability is not None:
            verb = 'killed'
            if self.ability.type == Ability.REVIVING_TYPE:
                verb = 'revived'
            if self.ability.type == Ability.DENYING_TYPE:
                verb = 'denied'
        else:
            verb = 'died'
        return 'Round {} at {}: {} {} {}'.format(self.round_id, self.time_point, self.killing_player, verb,
                                                    dying_entity)

    @property
    def event_type(self):
        if self.ability is None:
            return 'death'
        if self.ability.type == Ability.REVIVING_TYPE:
            return 'revive'
        if self.ability.type == Ability.DAMAGING_TYPE:
            return 'kill'
        if self.ability.type == Ability.DENYING_TYPE:
            return 'deny'

    @property
    def possible_dying_npcs(self):
        hero = self.dying_player.get_hero_at_timepoint(self.round, self.time_point)
        return hero.npc_set.all()

    @property
    def possible_killing_players(self):
        left_players = self.round.game.left_team.players.all()
        right_players = self.round.game.right_team.players.all()
        if self.event_type in ['death', 'kill', 'deny']:
            if self.dying_player in left_players:
                return right_players
            else:
                return left_players
        else:
            return []

    @property
    def possible_abilities(self):
        if self.killing_player is None:
            return []
        hero = self.killing_player.get_hero_at_timepoint(self.round, self.time_point)
        if hero == '':
            return []
        current_type = self.ability.type
        return hero.abilities.filter(type=current_type).all()

    @property
    def possible_assists(self):
        if self.killing_player is None:
            return []
        if self.ability is None or self.ability.type != Ability.DAMAGING_TYPE:
            return []
        left_players = self.round.game.left_team.players.all()
        if self.killing_player in left_players:
            return [x for x in left_players if x != self.killing_player]
        else:
            right_players = self.round.game.right_team.players.all()
            return [x for x in right_players if x != self.killing_player]


class Ultimate(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    gained = models.DecimalField(max_digits=6, decimal_places=1)
    used = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    ended = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)

    class Meta:
        ordering = ['round', 'gained', 'player']


class HeroPick(models.Model):
    time_point = models.DecimalField(max_digits=6, decimal_places=1)
    end_time_point = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    new_hero = models.ForeignKey(Hero, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return '{} switched to {} at {}'.format(self.player, self.new_hero, self.time_point)

    class Meta:
        unique_together = (("round", "time_point", "player", "new_hero"),)
        ordering = ['round', 'time_point', 'player']

