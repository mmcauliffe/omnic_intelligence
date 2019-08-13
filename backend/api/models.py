from django.db import models
import os
import re
import csv
from decimal import Decimal
from django.conf import settings
import subprocess

LEFT = 'L'
RIGHT = 'R'
NEITHER = 'N'
SIDE_CHOICES = (
    (LEFT, 'Left'),
    (RIGHT, 'Right'),
    (NEITHER, 'Neither'),
)


# Create your models here.

class StreamChannel(models.Model):
    SITE_CHOICES = (('T', 'Twitch'),
                    ('Y', 'YouTube'))
    name = models.CharField(max_length=256, unique=True)
    site = models.CharField(max_length=1, choices=SITE_CHOICES, default='T')
    youtube_channel_id = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.get_site_display())


class StreamVod(models.Model):
    ORIGINAL = 'O'
    FILM_FORMAT_CHOICES = ((ORIGINAL, 'Original'),
                           ('W', 'World Cup 2017'),
                           ('A', 'APEX'),
                           ('K', 'Korean Contenders'),
                           ('2', 'Overwatch league stage 2'))
    STATUS_CHOICES = (
        ('N', 'Not analyzed'),
        ('G', 'Automatically annotated for in-game/out-of-game'),
        ('A', 'Rounds automatically annotated'),
        ('T', 'Game boundaries manually checked'),
        ('M', 'Round events manually corrected')
                      )
    TYPE_CHOICES = (
        ('M', 'Match'),
        ('G', 'Game'),
        ('R', 'Round')
    )
    channel = models.ForeignKey(StreamChannel, on_delete=models.CASCADE)
    url = models.URLField(max_length=256, unique=True)
    title = models.CharField(max_length=256)
    broadcast_date = models.DateTimeField(blank=True, null=True)
    film_format = models.CharField(max_length=1, choices=FILM_FORMAT_CHOICES, default=ORIGINAL)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='M')
    last_modified = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

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
    hero_type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    class Meta:
        verbose_name_plural = "heroes"
        ordering = ['hero_type', 'name']

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=128, unique=True)

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
    heroes = models.ManyToManyField(Hero, related_name='abilities')
    name = models.CharField(max_length=128)
    revive_ability = models.BooleanField(default=False)
    damaging_ability = models.BooleanField(default=True)
    headshot_capable = models.BooleanField(default=False)
    ultimate_ability = models.BooleanField(default=False)
    matrixable = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "abilities"
        ordering = ['name']

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=128)
    liquipedia_id = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_hero_at_timepoint(self, round_object, time_point):
        time_point = round(time_point, 1)
        s = self.switch_set.filter(time_point__lte=time_point, round=round_object).order_by(
            '-time_point').prefetch_related('new_hero', 'new_hero__abilities').first()
        if s is not None:
            return s.new_hero
        return ''

    def get_ult_states(self, round_object):
        ultgains = self.ultgain_set.filter(round=round_object).all()
        round_end = round(round_object.end - round_object.begin, 1)
        if len(ultgains) == 0:
            return [{'begin': 0, 'end': round_end, 'status': 'no_ult'}]

        ultuses = self.ultuse_set.filter(round=round_object).all()
        ultends = self.ultend_set.filter(round=round_object).all()
        switches = self.switch_set.filter(round=round_object).all()
        starts = sorted([round(x.time_point, 1) for x in ultgains])
        switch_time_points = [round(x.time_point, 1) for x in switches]
        ult_end_time_points = [round(x.time_point, 1) for x in ultends]
        ends = sorted([round(x.time_point, 1) for x in ultuses] + switch_time_points)
        segments = []
        show_using_ults = round_object.game.match.event.spectator_mode == 'S'
        for i, s in enumerate(starts):
            if segments:
                segments.append({'begin': segments[-1]['end'], 'end': s, 'status': 'no_ult'})
            else:
                segments.append({'begin': 0, 'end': s, 'status': 'no_ult'})
            for e in ends:
                if e >= s:
                    segments.append({'begin': s, 'end': e, 'status': 'has_ult'})
                    if e not in switch_time_points and ultends:
                        for ue in ult_end_time_points:
                            if ue >= e and (i == len(starts) -1 or (ue >= s)):
                                segments.append({'begin': e, 'end': ue, 'status': 'using_ult'})
                                break
                    break
            else:
                segments.append({'begin': s, 'end': round_end, 'status': 'has_ult'})
        if segments[-1]['end'] < round_end:
            segments.append({'begin': segments[-1]['end'], 'end': round_end, 'status': 'no_ult'})
        return segments

    def get_alive_states(self, round_object):
        deaths = self.death_set.filter(round=round_object).all()
        round_end = round_object.end - round_object.begin
        if len(deaths) == 0:
            return [{'begin': 0, 'end': round_end, 'status': 'alive'}]
        revives = self.revived_player.filter(round=round_object).all()
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

    def get_status_effect_states(self, round_object, status):
        status_effects = self.statuseffect_set.filter(round=round_object, status=status).all()
        round_end = round_object.end - round_object.begin
        status_name = status.name.lower()
        if len(status_effects) == 0:
            return [{'begin': 0, 'end': round_end, 'status': 'not_'+ status_name}]
        segments = []
        for s in status_effects:
            if segments:
                segments.append({'begin': segments[-1]['end'], 'end': s.start_time, 'status': 'not_'+status_name})
            else:
                segments.append({'begin': Decimal('0.0'), 'end':  s.start_time, 'status': 'not_'+status_name})
            segments.append({'begin': s.start_time, 'end': s.end_time, 'status': status_name})
        if segments[-1]['end'] < round_end:
            segments.append({'begin': segments[-1]['end'], 'end': round_end, 'status': 'not_'+status_name})
        return segments

    def get_hero_states(self, round_object):
        switches = self.switch_set.filter(round=round_object).all()
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

    def get_ult_at_timepoint(self, round_object, time_point):
        time_point = round(time_point, 1)
        last_ult_gain = UltGain.objects.filter(time_point__lte=time_point, round=round_object,
                                               player=self).order_by(
            '-time_point').first()
        if last_ult_gain is None:
            return False
        last_ult_gain = round(last_ult_gain.time_point, 1)
        last_ult_use = UltUse.objects.filter(time_point__lte=time_point, round=round_object,
                                             player=self).order_by(
            '-time_point').first()
        if last_ult_use is not None and time_point == round(last_ult_use.time_point, 1) == last_ult_gain:
            return True
        elif last_ult_use is not None and round(last_ult_use.time_point, 1) >= last_ult_gain:
            return False
        last_switch = Switch.objects.filter(time_point__lte=time_point, round=round_object,
                                            player=self).order_by(
            '-time_point').first()
        if last_switch is not None and round(last_switch.time_point, 1) >= last_ult_gain:
            return False
        return True

    def get_alive_at_timepoint(self, round_object, time_point):
        time_point = round(time_point, 1)
        last_death = Death.objects.filter(time_point__lte=time_point, round=round_object, player=self).order_by(
            '-time_point').first()
        if last_death is None:
            return True
        last_death_time = round(last_death.time_point, 1)
        respawn_time = last_death.time_point + 10
        if round_object.is_overtime(time_point):
            respawn_time += 2
        respawn_time = round(respawn_time, 1)
        if time_point >= respawn_time:
            return True
        last_revive = Revive.objects.filter(time_point__lte=respawn_time, time_point__gte=last_death_time,
                                            round=round_object, revived_player=self).order_by(
            '-time_point').first()
        if last_revive is not None:
            last_revive_time = round(last_revive.time_point, 1)
            if respawn_time >= last_revive_time >= last_death_time and last_revive_time <= time_point:
                return True
        return False

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
    SPECTATOR_MODE_CHOICES = (('O', 'Original'),
                              ('W', 'World Cup'),
                              ('L', 'Overwatch League'),
                              ('C', 'Contenders'),)
    name = models.CharField(max_length=128)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    liquipedia_id = models.CharField(max_length=128, null=True, blank=True)
    spectator_mode = models.CharField(max_length=1, choices=SPECTATOR_MODE_CHOICES, default='S')
    stream_channels = models.ManyToManyField(StreamChannel, related_name='events')
    teams = models.ManyToManyField(Team, through='EventParticipation')
    channel_query_string = models.CharField(max_length=128, null=True, blank=True)

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
    rules = models.CharField(max_length=1, choices=RULES_CHOICES, default=COMP)
    exhibition = models.BooleanField(default=False)

    def __str__(self):
        return 'Match between {} in {}'.format(' and '.join(x.name for x in self.teams.all()), str(self.event))

    class Meta:
        ordering = ['-id']
        verbose_name_plural = "matches"

    @property
    def team_description(self):
        return ' and '.join(x.name for x in self.teams.all())

    @property
    def date(self):
        return self.game_set.first().round_set.first().streamvod_set.first().published_at.date()

    @property
    def start_time(self):
        first_game = self.game_set.first()
        if first_game is not None:
            first_round = first_game.round_set.first()
            if first_round is not None:
                return first_round.begin
        return 0


class Game(models.Model):
    game_number = models.IntegerField()
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    left_team = models.OneToOneField('TeamParticipation', on_delete=models.CASCADE, related_name='left_team')
    right_team = models.OneToOneField('TeamParticipation', on_delete=models.CASCADE, related_name='right_team')
    map = models.ForeignKey(Map, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("match", "game_number"),)
        ordering = ['-match__id', 'game_number']


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
    color = models.CharField(max_length=1, choices=COLOR_CHOICES, default=BLUE)
    points = models.IntegerField(null=True, blank=True)
    subpoints = models.CharField(max_length=128, null=True, blank=True)
    players = models.ManyToManyField(Player, through='PlayerParticipation')

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
    begin = models.DecimalField(max_digits=6, decimal_places=1, default=Decimal('0.0'))
    end = models.DecimalField(max_digits=6, decimal_places=1, default=Decimal('0.0'))
    annotation_status = models.CharField(max_length=1, choices=ANNOTATION_CHOICES, default='N')

    class Meta:
        unique_together = (("game", "round_number"),)
        ordering = ['game__match__id', 'game__game_number', 'round_number']

    def __str__(self):
        return 'Round {} of Game {} for {} vs {} in {}'.format(self.round_number, self.game.game_number,
                                                               self.game.left_team.team, self.game.right_team.team,
                                                               self.game.match.event)

    def fix_switch_end_points(self):
        switches = self.switch_set.order_by('-time_point').prefetch_related('player').all()
        last_switches = {}
        for s in switches:
            if s.player.id not in last_switches:
                if s.end_time_point != self.end:
                    s.end_time_point = self.end
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

    def get_nonkill_deaths(self):
        deaths = self.death_set.prefetch_related('player').all()
        nonkills = []
        for d in deaths:
            try:
                k = Kill.objects.get(round=self, time_point=d.time_point,
                                     killed_player=d.player)
            except Kill.DoesNotExist:
                nonkills.append(d)
        return nonkills

    def get_nonkill_npcdeaths(self):
        deaths = self.npcdeath_set.prefetch_related('npc').all()
        nonkills = []
        for d in deaths:
            try:
                k = KillNPC.objects.get(round=self, time_point=d.time_point, killed_npc=d.npc)
            except KillNPC.DoesNotExist:
                nonkills.append(d)
        return nonkills

    def get_player_states(self):
        data = {'left': {}, 'right': {}}
        left_team = self.game.left_team.playerparticipation_set.prefetch_related('player', 'player__switch_set',
                                                                                 'player__death_set',
                                                                                 'player__statuseffect_set',
                                                                                 'player__ultuse_set',
                                                                                 'player__ultgain_set',
                                                                                 'player__ultend_set',
                                                                                 'player__revived_player').all()
        right_team = self.game.right_team.playerparticipation_set.all()
        statuses = Status.objects.all()
        for p in left_team:
            pp = p.player
            hero_states = pp.get_hero_states(self)

            data['left'][p.player_index] = {'ult': pp.get_ult_states(self), 'alive': pp.get_alive_states(self),
                                            'hero': hero_states, 'player': pp.name}
            for s in statuses:
                data['left'][p.player_index][s.name.lower()] = pp.get_status_effect_states(self, s)
        for p in right_team:
            pp = p.player
            hero_states = pp.get_hero_states(self)
            data['right'][p.player_index] = {'ult': pp.get_ult_states(self), 'alive': pp.get_alive_states(self),
                                             'hero': hero_states, 'player': pp.name}
            for s in statuses:
                data['right'][p.player_index][s.name.lower()] = pp.get_status_effect_states(self, s)
        return data

    def get_heroes_used(self):
        from .utils import transform_oi_heroes
        used_heroes = {}
        q = self.switch_set.order_by('player_id', 'time_point').all()
        cur_player = None
        cur_time = 0
        cur_hero = None
        for r in q:
            if cur_player is None:
                cur_player = r.player_id
            if cur_hero is None:
                cur_hero = transform_oi_heroes(r.new_hero.name)
            if cur_hero is not None:
                if cur_hero not in used_heroes:
                    used_heroes[cur_hero] = 0
            if r.player_id != cur_player:
                if cur_player is not None:
                    used_heroes[cur_hero] += self.end - cur_time - self.begin
                cur_player = r.player_id
                cur_time = r.time_point
                if r.new_hero is not None:
                    cur_hero = transform_oi_heroes(r.new_hero.name)
            elif cur_hero is not None and transform_oi_heroes(r.new_hero.name) != cur_hero:
                used_heroes[cur_hero] += r.time_point - cur_time
                cur_time = r.time_point
                cur_hero = transform_oi_heroes(r.new_hero.name)
        if cur_hero not in used_heroes:
            used_heroes[cur_hero] = 0
        used_heroes[cur_hero] += self.end - cur_time - self.begin

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
        if len(replays) == 0 and len(pauses) == 0:
            return [[0, self.end - self.begin]]
        interruptions = sorted([x for x in replays] + [x for x in pauses], key=lambda x: x.start_time)

        round_end = Decimal(self.end - self.begin)
        cur_beg = Decimal('0.00')
        segments = []
        for i, s in enumerate(interruptions):
            segments.append([cur_beg, s.start_time])
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

    def get_overtime_states(self):
        overtimes = self.overtime_set.all()
        round_end = self.end - self.begin
        if len(overtimes) == 0:
            return [{'begin': 0, 'end': round_end, 'status': 'not_overtime'}]

        states = []
        for o in overtimes:
            if not states:
                states.append({'begin': 0, 'end': o.start_time, 'status': 'not_overtime'})
            states.append({'begin': o.start_time, 'end': o.end_time, 'status': 'overtime'})
        if states[-1]['end'] is None:
            states[-1]['end'] = round_end
        elif states[-1]['end'] != round_end:
            states.append({'begin': states[-1]['end'], 'end': round_end, 'status': 'not_overtime'})
        return states

    def get_pause_states(self):
        pauses = self.pause_set.all()
        round_end = self.end - self.begin
        if len(pauses) == 0:
            return [{'begin': 0, 'end': round_end, 'status': 'not_paused'}]
        states = []
        for o in pauses:
            if not states:
                states.append({'begin': 0, 'end': o.start_time, 'status': 'not_paused'})
            states.append({'begin': o.start_time, 'end': o.end_time, 'status': 'paused'})
        if states[-1]['end'] is None:
            states[-1]['end'] = round_end
        elif states[-1]['end'] != round_end:
            states.append({'begin': states[-1]['end'], 'end': round_end, 'status': 'not_paused'})
        return states

    def get_replay_states(self):
        replays = self.replay_set.all()
        round_end = self.end - self.begin
        if len(replays) == 0:
            return [{'begin': 0, 'end': round_end, 'status': 'not_replay'}]
        states = []
        for o in replays:
            if not states:
                states.append({'begin': 0, 'end': o.start_time, 'status': 'not_replay'})
            states.append({'begin': o.start_time, 'end': o.end_time, 'status': 'replay'})
        if states[-1]['end'] is None:
            states[-1]['end'] = round_end
        elif states[-1]['end'] != round_end:
            states.append({'begin': states[-1]['end'], 'end': round_end, 'status': 'not_replay'})
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
        kills = self.kill_set.all()
        for k in kills:
            killing_hero = k.killing_player.get_hero_at_timepoint(self, k.time_point).name
            if self.game.left_team.playerparticipation_set.filter(player=k.killing_player).count():
                killing_color = self.game.left_team.get_color_display()
                dying_color = self.game.right_team.get_color_display()
            else:
                killing_color = self.game.right_team.get_color_display()
                dying_color = self.game.left_team.get_color_display()
            assisting_players = k.assisting_players.all()
            assisting_heroes = []
            for p in assisting_players:
                assisting_heroes.append(p.get_hero_at_timepoint(self, k.time_point).name)
            dying_hero = k.killed_player.get_hero_at_timepoint(self, k.time_point).name
            potential_killfeed.append(
                {'time_point': k.time_point, 'first_hero': killing_hero, 'first_player': k.killing_player.name,
                 'first_color': killing_color, 'assisting_heroes': assisting_heroes,
                 'ability': k.ability.name, 'headshot': k.headshot,
                 'second_hero': dying_hero, 'second_player': k.killed_player.name, 'second_color': dying_color})
        for u in self.ultdenial_set.all():
            denying_hero = u.denying_player.get_hero_at_timepoint(self, u.time_point)
            if self.game.left_team.playerparticipation_set.filter(player=u.denying_player).count():
                killing_color = self.game.left_team.get_color_display()
                dying_color = self.game.right_team.get_color_display()
            else:
                killing_color = self.game.right_team.get_color_display()
                dying_color = self.game.left_team.get_color_display()
            ability = denying_hero.abilities.get(name='Defense Matrix').name
            kf_item = {'time_point': u.time_point, 'first_hero': denying_hero.name, 'first_player': u.denying_player.name,
                       'ability':ability, 'second_hero': u.ability.name, 'headshot': False,
                     'assisting_heroes': [],
                       'first_color': killing_color,'second_player': u.denied_player.name, 'second_color': dying_color}
            potential_killfeed.append(kf_item)

        killnpcs = self.killnpc_set.all()
        for k in killnpcs:
            killing_hero = k.killing_player.get_hero_at_timepoint(self, k.time_point).name
            dying_player = 'N/A'
            if self.game.left_team.playerparticipation_set.filter(player=k.killing_player).count():
                killing_color = self.game.left_team.get_color_display()
                dying_color = self.game.right_team.get_color_display()
                for p in self.game.right_team.players.all():
                    if p.get_hero_at_timepoint(self, k.time_point) == k.killed_npc.spawning_hero:
                        dying_player = p.name
                        break
            else:
                killing_color = self.game.right_team.get_color_display()
                dying_color = self.game.left_team.get_color_display()
                for p in self.game.left_team.players.all():

                    if p.get_hero_at_timepoint(self, k.time_point) == k.killed_npc.spawning_hero:
                        dying_player = p.name
                        break
            assisting_players = k.assisting_players.all()
            assisting_heroes = []
            for p in assisting_players:
                assisting_heroes.append(p.get_hero_at_timepoint(self, k.time_point).name)
            dying_npc = k.killed_npc.name
            potential_killfeed.append(
                {'time_point': k.time_point, 'first_hero': killing_hero, 'first_player': k.killing_player.name,
                 'first_color': killing_color, 'assisting_heroes': assisting_heroes, 'ability': k.ability.name,
                 'headshot': False, 'second_hero': dying_npc,
                 'second_player': dying_player, 'second_color': dying_color})
        deaths = self.death_set.all()
        for d in deaths:
            for k in kills:
                if d.time_point == k.time_point and d.player == k.killed_player:
                    break
            else:
                dying_hero = d.player.get_hero_at_timepoint(self, d.time_point).name
                if self.game.left_team.playerparticipation_set.filter(player=d.player).count():
                    dying_color = self.game.left_team.get_color_display()
                else:
                    dying_color = self.game.right_team.get_color_display()
                potential_killfeed.append(
                    {'time_point': d.time_point, 'first_hero': 'N/A', 'first_player': 'N/A', 'first_color': 'N/A',
                     'assisting_heroes': [],
                     'ability': 'primary', 'headshot': False, 'second_hero': dying_hero, 'second_player': d.player.name,
                     'second_color': dying_color})
        npcdeaths = self.npcdeath_set.all()
        for d in npcdeaths:
            for k in killnpcs:
                if d.time_point == k.time_point and d.npc == k.killed_npc:
                    break
            else:
                dying_npc = d.npc.name
                dying_player = 'N/A'
                if d.side == 'L':
                    dying_color = self.game.left_team.get_color_display()
                    for p in self.game.left_team.players.all():
                        if p.get_hero_at_timepoint(self, d.time_point) == d.npc.spawning_hero:
                            dying_player = p.name
                            break
                else:
                    dying_color = self.game.right_team.get_color_display()
                    for p in self.game.right_team.players.all():
                        if p.get_hero_at_timepoint(self, d.time_point) == d.npc.spawning_hero:
                            dying_player = p.name
                            break
                potential_killfeed.append(
                    {'time_point': d.time_point, 'first_hero': 'N/A', 'first_player': 'N/A', 'first_color': 'N/A',
                     'assisting_heroes': [],
                     'ability': 'primary', 'headshot': False, 'second_hero': dying_npc, 'second_player': dying_player,
                     'second_color': dying_color})
        revives = self.revive_set.all()
        for r in revives:
            reviving_hero = r.reviving_player.get_hero_at_timepoint(self, r.time_point).name
            if self.game.left_team.playerparticipation_set.filter(player=r.reviving_player).count():
                reviving_color = self.game.left_team.get_color_display()
            else:
                reviving_color = self.game.right_team.get_color_display()
            revived_hero = r.revived_player.get_hero_at_timepoint(self, r.time_point).name
            potential_killfeed.append(
                {'time_point': r.time_point, 'first_hero': reviving_hero, 'first_player': r.reviving_player.name,
                 'first_color': reviving_color, 'assisting_heroes': [], 'ability': r.ability.name, 'headshot': False,
                 'second_hero': revived_hero, 'second_player': r.revived_player.name, 'second_color': reviving_color})
        potential_killfeed = sorted(potential_killfeed, key=lambda x: x['time_point'])
        return potential_killfeed

    def for_wl(self):
        annotations = [[self.begin, 'MATCH']]
        for s in self.switch_set.all():
            side, ind = self.get_side_and_index(s.player)
            if side == 'L':
                color = 'BLUE'
            else:
                color = 'RED'
            try:
                old_hero = s.player.get_hero_at_timepoint(self, s.time_point - 1).name.lower()
            except:
                old_hero = ''
            annotations.append([s.time_point + self.begin, 'SWITCH', color, ind + 1, old_hero, s.new_hero.name.lower()])
        for k in self.kill_set.all():
            side, ind = self.get_side_and_index(k.killing_player)
            killed_side, killed_ind = self.get_side_and_index(k.killed_player)
            if side == 'L':
                color = 'BLUE'
            else:
                color = 'RED'
            killing_hero = k.killing_player.get_hero_at_timepoint(self, k.time_point).name.lower()
            killed_hero = k.killed_player.get_hero_at_timepoint(self, k.time_point).name.lower()
            method = k.ability.name.lower()
            if method == 'primary':
                method = ''
            headshot = ''
            if k.headshot:
                headshot = 'headshot'
            annotations.append(
                [k.time_point + self.begin, 'KILL', color, ind + 1, killing_hero, killed_ind + 1, killed_hero, method,
                 headshot])
        for k in self.killnpc_set.all():

            side, ind = self.get_side_and_index(k.killing_player)
            if side == 'L':
                color = 'BLUE'
            else:
                color = 'RED'
            killing_hero = k.killing_player.get_hero_at_timepoint(self, k.time_point).name.lower()
            method = k.ability.name.lower()
            if method == 'primary':
                method = ''
            headshot = ''
            annotations.append(
                [k.time_point + self.begin, 'KILL', color, ind + 1, killing_hero, 0, k.killed_npc.name.lower(), method,
                 headshot])
        for r in self.revive_set.all():
            side, ind = self.get_side_and_index(r.reviving_player)
            revived_side, revived_ind = self.get_side_and_index(r.revived_player)
            if side == 'L':
                color = 'BLUE'
            else:
                color = 'RED'
            reviving_hero = r.reviving_player.get_hero_at_timepoint(self, r.time_point).name.lower()
            revived_hero = r.revived_player.get_hero_at_timepoint(self, r.time_point).name.lower()
            method = r.ability.name.lower()
            annotations.append(
                [r.time_point + self.begin, 'REVIVE', color, ind + 1, reviving_hero, revived_ind + 1, revived_hero,
                 method])
        for d in self.death_set.all():
            side, ind = self.get_side_and_index(d.player)
            hero = d.player.get_hero_at_timepoint(self, d.time_point)
            if side == 'L':
                color = 'BLUE'
            else:
                color = 'RED'
            annotations.append([d.time_point + self.begin, 'DEATH', color, ind + 1, hero.name.lower()])
        for d in self.npcdeath_set.all():
            if d.side == 'L':
                color = 'BLUE'
            else:
                color = 'RED'

            annotations.append([d.time_point + self.begin, 'DEATH', color, 0, d.npc.name.lower()])
        for u in self.ultgain_set.all():
            side, ind = self.get_side_and_index(u.player)
            if side == 'L':
                color = 'BLUE'
            else:
                color = 'RED'
            hero = u.player.get_hero_at_timepoint(self, u.time_point)
            annotations.append([u.time_point + self.begin, 'ULT_GAIN', color, ind + 1, hero.name.lower()])
        for u in self.ultuse_set.all():
            side, ind = self.get_side_and_index(u.player)
            if side == 'L':
                color = 'BLUE'
            else:
                color = 'RED'
            hero = u.player.get_hero_at_timepoint(self, u.time_point)
            annotations.append([u.time_point + self.begin, 'ULT_USE', color, ind + 1, hero.name.lower()])
        for p in self.pause_set.all():
            annotations.append([p.start_time + self.begin, 'PAUSE'])
            annotations.append([p.end_time + self.begin, 'UNPAUSE'])
        for p in self.pointgain_set.all():
            if self.attacking_side == 'L':
                color = 'BLUE'
            else:
                color = 'RED'
            annotations.append([p.time_point + self.begin, "POINTS", color, p.point_total])
        for p in self.pointflip_set.all():
            if p.controlling_side == 'L':
                color = 'BLUE'
            else:
                color = 'RED'
            annotations.append([p.time_point + self.begin, "ATTACK", color])
        return sorted(annotations)

    def construct_kf_at_time(self, time_point):
        time_point = time_point
        potential_killfeed = []
        time_window = 7.2
        kills = self.kill_set.filter(time_point__gte=time_point - time_window, time_point__lte=time_point).all()
        for k in kills:
            killing_hero = k.killing_player.get_hero_at_timepoint(self, k.time_point).name
            if self.game.left_team.playerparticipation_set.filter(player=k.killing_player).count():
                killing_color = self.game.left_team.get_color_display()
                dying_color = self.game.right_team.get_color_display()
            else:
                killing_color = self.game.right_team.get_color_display()
                dying_color = self.game.left_team.get_color_display()
            dying_hero = k.killed_player.get_hero_at_timepoint(self, k.time_point).name
            potential_killfeed.append(
                [k.time_point, killing_hero, killing_color, k.ability.name, k.headshot, dying_hero, dying_color])
        killnpcs = self.killnpc_set.filter(time_point__gte=time_point - time_window, time_point__lte=time_point).all()
        for k in killnpcs:
            killing_hero = k.killing_player.get_hero_at_timepoint(self, k.time_point).name
            if self.game.left_team.playerparticipation_set.filter(player=k.killing_player).count():
                killing_color = self.game.left_team.get_color_display()
                dying_color = self.game.right_team.get_color_display()
            else:
                killing_color = self.game.right_team.get_color_display()
                dying_color = self.game.left_team.get_color_display()
            dying_npc = k.killed_npc.name
            potential_killfeed.append(
                [k.time_point, killing_hero, killing_color, k.ability.name, False, dying_npc, dying_color])
        deaths = self.death_set.filter(time_point__gte=time_point - time_window, time_point__lte=time_point).all()
        for d in deaths:
            for k in kills:
                if d.time_point == k.time_point and d.player == k.killed_player:
                    break
            else:
                dying_hero = d.player.get_hero_at_timepoint(self, d.time_point).name
                if self.game.left_team.playerparticipation_set.filter(player=d.player).count():
                    dying_color = self.game.left_team.get_color_display()
                else:
                    dying_color = self.game.right_team.get_color_display()
                potential_killfeed.append([d.time_point, 'N/A', 'N/A', 'primary', False, dying_hero, dying_color])
        npcdeaths = self.npcdeath_set.filter(time_point__gte=time_point - time_window, time_point__lte=time_point).all()
        for d in npcdeaths:
            for k in killnpcs:
                if d.time_point == k.time_point and d.npc == k.killed_npc:
                    break
            else:
                dying_npc = d.npc.name
                if d.side == 'L':
                    dying_color = self.game.left_team.get_color_display()
                else:
                    dying_color = self.game.right_team.get_color_display()
                potential_killfeed.append([d.time_point, 'N/A', 'N/A', 'primary', False, dying_npc, dying_color])
        revives = self.revive_set.filter(time_point__gte=time_point - time_window, time_point__lte=time_point).all()
        for r in revives:
            reviving_hero = r.reviving_player.get_hero_at_timepoint(self, r.time_point).name
            if self.game.left_team.playerparticipation_set.filter(player=r.reviving_player).count():
                reviving_color = self.game.left_team.get_color_display()
            else:
                reviving_color = self.game.right_team.get_color_display()
            revived_hero = r.revived_player.get_hero_at_timepoint(self, r.time_point).name
            potential_killfeed.append(
                [r.time_point, reviving_hero, reviving_color, r.ability.name, False, revived_hero, reviving_color])
        potential_killfeed = sorted(potential_killfeed, key=lambda x: -1 * x[0])
        return potential_killfeed[:6]


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


class Switch(models.Model):
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


class Death(models.Model):
    time_point = models.DecimalField(max_digits=6, decimal_places=1)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "time_point", "player"),)
        ordering = ['round', 'time_point', 'player']

    def __str__(self):
        return '{} died at {}'.format(self.player, self.time_point)


class NPCDeath(models.Model):
    time_point = models.DecimalField(max_digits=6, decimal_places=1)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    npc = models.ForeignKey(NPC, on_delete=models.CASCADE)
    side = models.CharField(max_length=1, choices=SIDE_CHOICES, default=NEITHER)

    def __str__(self):
        return '{} died at {}'.format(self.npc, self.time_point)

    class Meta:
        unique_together = (("round", "time_point", "npc", "side"),)
        ordering = ['round', 'time_point', 'side', 'npc']


class UltGain(models.Model):
    time_point = models.DecimalField(max_digits=6, decimal_places=1)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    def __str__(self):
        return '{} gained their ult at {}'.format(self.player, self.time_point)

    class Meta:
        unique_together = (("round", "time_point", "player"),)
        ordering = ['round', 'time_point', 'player']


class UltUse(models.Model):
    time_point = models.DecimalField(max_digits=6, decimal_places=1)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    def __str__(self):
        return '{} used their ult at {}'.format(self.player, self.time_point)

    class Meta:
        unique_together = (("round", "time_point", "player"),)
        ordering = ['round', 'time_point', 'player']


class UltEnd(models.Model):
    time_point = models.DecimalField(max_digits=6, decimal_places=1)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    def __str__(self):
        return '{} ended their ult at {}'.format(self.player, self.time_point)

    class Meta:
        unique_together = (("round", "time_point", "player"),)
        ordering = ['round', 'time_point', 'player']


class Kill(models.Model):
    time_point = models.DecimalField(max_digits=6, decimal_places=1)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    killing_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='kills')
    assisting_players = models.ManyToManyField(Player, related_name='assisted_kills')
    killed_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='killeds')
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE)
    headshot = models.BooleanField(default=False)

    def get_corresponding_death(self):
        return Death.objects.filter(round=self.round,
                                    time_point=self.time_point,
                                    player=self.killed_player).first()

    def __str__(self):
        return '{} killed {} at {}'.format(self.killing_player, self.killed_player, self.time_point)

    class Meta:
        unique_together = (("round", "time_point", "killing_player", "killed_player"),)
        ordering = ['round', 'time_point', 'killing_player', 'killed_player']

    def save(self, *args, **kwargs):
        super(Kill, self).save(*args, **kwargs)  # Call the "real" save() method.
        d = Death.objects.get_or_create(time_point=self.time_point, player=self.killed_player, round=self.round)

    @property
    def possible_abilities(self):
        hero = self.killing_player.get_hero_at_timepoint(self.round, self.time_point)
        if hero == '':
            return []
        return hero.abilities.filter(damaging_ability=True).all()

    @property
    def possible_assists(self):
        left_players = self.round.game.left_team.players.all()
        if self.killing_player in left_players:
            return [x for x in left_players if x != self.killing_player]
        else:
            right_players = self.round.game.right_team.players.all()
            return [x for x in right_players if x != self.killing_player]


class UltDenial(models.Model):
    time_point = models.DecimalField(max_digits=6, decimal_places=1)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    denying_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='ult_denials')
    denied_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='denied_ults')
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE)


class KillNPC(models.Model):
    time_point = models.DecimalField(max_digits=6, decimal_places=1)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    killing_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='npc_kills')
    assisting_players = models.ManyToManyField(Player, related_name='assisted_npc_kills')
    killed_npc = models.ForeignKey(NPC, on_delete=models.CASCADE, related_name='killeds')
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE)

    def get_corresponding_death(self):
        return NPCDeath.objects.filter(round=self.round,
                                       time_point=self.time_point,
                                       npc=self.killed_npc,
                                       side=self.killed_npc_side).first()

    @property
    def possible_abilities(self):
        hero = self.killing_player.get_hero_at_timepoint(self.round, self.time_point)
        return hero.abilities.filter(damaging_ability=True).all()

    @property
    def possible_assists(self):
        left_players = self.round.game.left_team.players.all()
        if self.killing_player in left_players:
            return [x for x in left_players if x != self.killing_player]
        else:
            right_players = self.round.game.right_team.players.all()
            return [x for x in right_players if x != self.killing_player]

    def __str__(self):
        return '{} killed {} at {}'.format(self.killing_player, self.killed_npc, self.time_point)

    class Meta:
        unique_together = (("round", "time_point", "killing_player", "killed_npc"),)
        ordering = ['round', 'time_point', 'killing_player', 'killed_npc']

    @property
    def killed_npc_side(self):
        if self.round.game.left_team.players.filter(id=self.killing_player.id).count() > 0:
            return 'R'
        return 'L'

    def save(self, *args, **kwargs):
        super(KillNPC, self).save(*args, **kwargs)  # Call the "real" save() method.
        d = NPCDeath.objects.get_or_create(time_point=self.time_point, npc=self.killed_npc, round=self.round,
                                           side=self.killed_npc_side)


class Revive(models.Model):
    time_point = models.DecimalField(max_digits=6, decimal_places=1)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    reviving_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='reviving_player')
    revived_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='revived_player')
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "time_point", "reviving_player", "revived_player"),)
        ordering = ['round', 'time_point', 'reviving_player', 'revived_player']

    def __str__(self):
        return '{} revived {} at {}'.format(self.reviving_player, self.revived_player, self.time_point)