from django.core.management.base import BaseCommand, CommandError
from backend.api import models


def get_old_ult_states(self, round_object):
    ultgains = self.ultgain_set.filter(round=round_object).all()
    round_end = round(round_object.end - round_object.begin, 1)
    if len(ultgains) == 0:
        return [{'begin': 0, 'end': round_end, 'status': 'no_ult'}]

    ultuses = self.ultuse_set.filter(round=round_object).all()
    ultends = self.ultend_set.filter(round=round_object).all()
    switches = self.heropick_set.filter(round=round_object).all()
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
                        if ue >= e and (i == len(starts) - 1 or (ue >= s)):
                            segments.append({'begin': e, 'end': ue, 'status': 'using_ult'})
                            break
                break
        else:
            segments.append({'begin': s, 'end': round_end, 'status': 'has_ult'})
    if segments[-1]['end'] < round_end:
        segments.append({'begin': segments[-1]['end'], 'end': round_end, 'status': 'no_ult'})
    return segments


class Command(BaseCommand):
    help = "Convert"

    def handle(self, *args, **options):
        models.Ultimate.objects.all().delete()
        for i, r in enumerate(models.Round.objects.filter(annotation_status__in=['M', 'O']).all()):
            players = [x for x in r.game.right_team.players.all()] + [x for x in r.game.left_team.players.all()]
            ultimates = []
            for p in players:
                print(p)
                ult_states = get_old_ult_states(p, r)
                for j, u in enumerate(ult_states):
                    used_at = None
                    ended_at = None
                    if u['status'] == 'has_ult':
                        gained_at = u['begin']
                        if u['end'] != r.end:
                            used_at = u['end']
                        if j != len(ult_states) - 1:
                            if ult_states[j+1]['status'] == 'no_ult':
                                ended_at = used_at
                            elif ult_states[j+1]['status'] == 'using_ult':
                                if ult_states[j+1]['end'] != r.end:
                                    ended_at = ult_states[j+1]['end']
                        ultimates.append(models.Ultimate(round=r, player=p, gained=gained_at,
                                                         used=used_at, ended=ended_at))
            models.Ultimate.objects.bulk_create(ultimates)