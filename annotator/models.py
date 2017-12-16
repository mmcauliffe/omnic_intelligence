from django.db import models
import os
import re

LEFT = 'L'
RIGHT = 'R'
NEITHER = 'N'
SIDE_CHOICES = (
    (LEFT, 'Left'),
    (RIGHT, 'Right'),
    (NEITHER, 'Neither'),
)


# Create your models here.

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
    OFFENSE = 'O'
    DEFENSE = 'D'
    TANK = 'T'
    SUPPORT = 'S'
    TYPE_CHOICES = (
        (OFFENSE, 'Offense'),
        (DEFENSE, 'Defense'),
        (TANK, 'Tank'),
        (SUPPORT, 'Support'),
    )
    name = models.CharField(max_length=128, unique=True)
    hero_type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    class Meta:
        verbose_name_plural = "heroes"

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
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    revive_ability = models.BooleanField(default=False)
    damaging_ability = models.BooleanField(default=True)
    headshot_capable = models.BooleanField(default=False)
    ultimate_ability = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "abilities"
        ordering = ['hero', 'name']

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=128)
    wl_id = models.IntegerField(null=True, blank=False, unique=True)

    def __str__(self):
        return self.name

    def get_hero_at_timepoint(self, round, time_point):
        s =Switch.objects.filter(time_point__lte=time_point, round=round, player=self).order_by('-time_point').prefetch_related('new_hero', 'new_hero__ability_set').first()
        if s is not None:
            return s.new_hero

    class Meta:
        ordering = ['name', 'wl_id']



class Team(models.Model):
    name = models.CharField(max_length=128)
    players = models.ManyToManyField(Player, through='Affiliation')
    wl_id = models.IntegerField(null=True, blank=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', 'wl_id']


class Affiliation(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)


class Event(models.Model):
    name = models.CharField(max_length=128)
    wl_id = models.IntegerField(null=True, blank=False, unique=True)

    def __str__(self):
        return self.name


class Match(models.Model):
    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL)
    teams = models.ManyToManyField(Team)
    vod = models.URLField(null=True, blank=True)
    local_location = models.CharField(max_length=256, null=True, blank=True)
    wl_id = models.IntegerField(null=True, blank=False, unique=True)

    def get_video_link(self):
        if self.local_location is not None and os.path.exists(self.local_location):
            return self.local_location
        return self.vod

    def get_twitch_id(self):
        m = re.match('https://www\.twitch\.tv/videos/(\d+)[?]?.*',self.vod)
        if m is not None:
            return m.groups()[0]

    class Meta:
        verbose_name_plural = "matches"


class Game(models.Model):
    game_number = models.IntegerField()
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Team, through='TeamParticipation')
    left_points = models.IntegerField()
    left_subpoints = models.CharField(max_length=128)
    right_points = models.IntegerField()
    right_subpoints = models.CharField(max_length=128)
    map = models.ForeignKey(Map, on_delete=models.CASCADE)
    vod = models.URLField(null=True, blank=True)
    local_location = models.CharField(max_length=256, null=True, blank=True)

    def get_video_link(self):
        if self.local_location is not None and os.path.exists(self.local_location):
            return self.local_location
        return self.vod

    def get_twitch_id(self):
        if self.vod is None:
            return self.match.get_twitch_id()
        m = re.match('https://www\.twitch\.tv/videos/(\d+)[?]?.*',self.vod)
        if m is not None:
            return m.groups()[0]

    class Meta:
        unique_together = (("match", "game_number"),)


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
        ('K', 'Black'),
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    color = models.CharField(max_length=1, choices=COLOR_CHOICES, default=BLUE)
    side = models.CharField(max_length=1, choices=SIDE_CHOICES, default=NEITHER)
    players = models.ManyToManyField(Player, through='PlayerParticipation')
    class Meta:
        ordering = ['side']
        unique_together = (("game", "side"),)


class PlayerParticipation(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team_participation = models.ForeignKey(TeamParticipation, on_delete=models.CASCADE)
    player_index = models.IntegerField()

    class Meta:
        ordering = ['player_index']
        unique_together = (("team_participation", "player_index"),)


class Round(models.Model):
    round_number = models.IntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    attacking_side = models.CharField(max_length=1, choices=SIDE_CHOICES, default=NEITHER)
    begin = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    vod = models.URLField(null=True, blank=True)
    local_location = models.CharField(max_length=256, null=True, blank=True)

    def get_video_link(self):
        if self.local_location is not None and os.path.exists(self.local_location):
            return self.local_location
        return self.vod

    def get_twitch_id(self):
        if self.vod is None:
            return self.game.get_twitch_id()
        m = re.match('https://www\.twitch\.tv/videos/(\d+)[?]?.*',self.vod)
        if m is not None:
            return m.groups()[0]

    class Meta:
        unique_together = (("game", "round_number"),)


class Pause(models.Model):
    time_point = models.IntegerField()
    round = models.ForeignKey(Round, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "time_point"),)


class Unpause(models.Model):
    time_point = models.IntegerField()
    round = models.ForeignKey(Round, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "time_point"),)


class PointGain(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    time_point = models.IntegerField()
    point_total = models.IntegerField()

    class Meta:
        unique_together = (("round", "time_point"),)


class PointFlip(models.Model):
    time_point = models.IntegerField()
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    controlling_side = models.CharField(max_length=1, choices=SIDE_CHOICES, default=NEITHER)

    class Meta:
        unique_together = (("round", "time_point"),)


class Switch(models.Model):
    time_point = models.IntegerField()
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    new_hero = models.ForeignKey(Hero, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = (("round", "time_point", "player", "new_hero"),)
        ordering = ['round', 'time_point', 'player']


class Death(models.Model):
    time_point = models.IntegerField()
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "time_point", "player"),)
        ordering = ['round', 'time_point', 'player']

    def __str__(self):
        return str(self.player) + ' ' + str(self.time_point)

class NPCDeath(models.Model):
    time_point = models.IntegerField()
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    npc = models.ForeignKey(NPC, on_delete=models.CASCADE)
    side = models.CharField(max_length=1, choices=SIDE_CHOICES, default=NEITHER)

    class Meta:
        unique_together = (("round", "time_point", "npc", "side"),)
        ordering = ['round', 'time_point', 'side', 'npc']


class UltGain(models.Model):
    time_point = models.IntegerField()
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "time_point", "player"),)
        ordering = ['round', 'time_point', 'player']


class UltUse(models.Model):
    time_point = models.IntegerField()
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "time_point", "player"),)
        ordering = ['round', 'time_point', 'player']


class Kill(models.Model):
    time_point = models.IntegerField()
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    killing_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='killing_player')
    killed_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='killed_player')
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE)
    headshot = models.BooleanField(default=False)

    class Meta:
        unique_together = (("round", "time_point", "killing_player", "killed_player"),)
        ordering = ['round', 'time_point', 'killing_player', 'killed_player']


class KillNPC(models.Model):
    time_point = models.IntegerField()
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    killing_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='npc_killing_player')
    killed_npc = models.ForeignKey(NPC, on_delete=models.CASCADE, related_name='killed_npc')
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "time_point", "killing_player", "killed_npc"),)
        ordering = ['round', 'time_point', 'killing_player', 'killed_npc']


class Revive(models.Model):
    time_point = models.IntegerField()
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    reviving_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='reviving_player')
    revived_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='revived_player')
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("round", "time_point", "reviving_player", "revived_player"),)
        ordering = ['round', 'time_point', 'reviving_player', 'revived_player']
