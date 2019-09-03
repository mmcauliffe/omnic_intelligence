from django.core.management.base import BaseCommand, CommandError
from backend.api import models


class Command(BaseCommand):
    help = "Convert"

    def handle(self, *args, **options):
        models.Ultimate.objects.all().delete()
        for i, r in enumerate(models.Round.objects.filter(annotation_status__in=['M', 'O']).all()):
            players = [x for x in r.game.right_team.players.all()] + [x for x in r.game.left_team.players.all()]
            ultimates = []
            for p in players:
                print(p)
                ult_states = p.get_ult_states(r)
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