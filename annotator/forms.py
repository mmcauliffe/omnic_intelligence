from djng.forms import NgModelFormMixin, NgModelForm, fields
from django import forms
from .models import TeamParticipation, PlayerParticipation, Switch, Death, Kill, KillNPC, NPCDeath, UltUse, UltGain, \
    PointFlip, PointGain, Pause, Unpause, Revive, Ability, Match
from crispy_forms.helper import FormHelper

class MatchForm(NgModelFormMixin, NgModelForm, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)
        setup_bootstrap_helpers(self)

    class Meta:
        model = Match
        fields = ('event', 'teams', 'vod', 'wl_id')

def setup_bootstrap_helpers(object):
    object.helper = FormHelper()
    object.helper.form_class = 'form-horizontal'
    object.helper.label_class = 'col-lg-3'
    object.helper.field_class = 'col-lg-8'


class TeamForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = TeamParticipation
        fields = ('team', 'color', 'side')


class PlayerForm(NgModelFormMixin, NgModelForm):
    order = fields.IntegerField(required=False, widget=fields.widgets.HiddenInput(), initial=0)

    class Meta:
        model = PlayerParticipation
        fields = ('player',)


class SwitchForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = Switch
        fields = ('time_point', 'player', 'new_hero')


class DeathForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = Death
        fields = ('time_point', 'player')


class KillForm(NgModelFormMixin, NgModelForm):
    ability = fields.ModelChoiceField(queryset=Ability.objects.filter(damaging_ability=True))

    class Meta:
        model = Kill
        fields = ('time_point', 'killing_player', 'killed_player', 'ability', 'headshot')


class ReviveForm(NgModelFormMixin, NgModelForm):
    ability = fields.ModelChoiceField(queryset=Ability.objects.filter(revive_ability=True))

    class Meta:
        model = Revive
        fields = ('time_point', 'reviving_player', 'revived_player', 'ability')


class KillNPCForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = KillNPC
        fields = ('time_point', 'killing_player', 'killed_npc', 'ability')


class NPCDeathForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = NPCDeath
        fields = ('time_point', 'npc', 'side')


class UltUseForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = UltUse
        fields = ('time_point', 'player')


class UltGainForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = UltGain
        fields = ('time_point', 'player')


class PointGainForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = PointGain
        fields = ('time_point', 'point_total')


class PauseForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = Pause
        fields = ('time_point',)


class UnpauseForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = Unpause
        fields = ('time_point',)


class PointFlipForm(NgModelFormMixin, NgModelForm):
    class Meta:
        model = PointFlip
        fields = ('time_point', 'controlling_side')
