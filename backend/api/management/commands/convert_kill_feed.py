from django.core.management.base import BaseCommand, CommandError
from backend.api import models


class Command(BaseCommand):
    help = "Convert"

    def handle(self, *args, **options):
        models.KillFeedEvent.objects.all().delete()
        for i, r in enumerate(models.Round.objects.filter(annotation_status__in=['M', 'O']).all()):
            print(i, r.id, r)
            kills = r.kill_set.all()
            kill_feed_events = []
            unique_set = set()
            for k in kills:
                unique_tuple = (k.round_id, k.time_point, k.killing_player_id, k.killed_player_id)
                if False and unique_tuple in unique_set:
                    print(kill_feed_events)
                    print(k)
                    raise(CommandError)
                unique_set.add(unique_tuple)

                assists = k.assisting_players.all()
                if not assists:
                    kill_feed_events.append(models.KillFeedEvent(time_point=k.time_point, round=k.round,
                                                                 killing_player=k.killing_player,
                                                                 dying_player=k.killed_player,
                                                                 ability=k.ability,
                                                                 headshot=k.headshot))
                else:
                    m = models.KillFeedEvent.objects.create(time_point=k.time_point, round=k.round,
                                                            killing_player=k.killing_player,
                                                            dying_player=k.killed_player,
                                                            ability=k.ability,
                                                            headshot=k.headshot)
                    for assisting_player in assists:
                        m.assisting_players.add(assisting_player)
            deaths = r.get_nonkill_deaths()
            for d in deaths:
                unique_tuple = (d.round_id, d.time_point, None, d.player_id)
                if False and unique_tuple in unique_set:
                    print(kill_feed_events)
                    print(d)
                    raise(CommandError)
                unique_set.add(unique_tuple)

                kill_feed_events.append(models.KillFeedEvent(time_point=d.time_point, round=d.round,
                                                             dying_player=d.player))
            kills = r.killnpc_set.all()
            for k in kills:
                assists = k.assisting_players.all()
                dying_side = 'left' if k.killed_npc_side == 'L' else 'right'
                dying_player = r.get_player_of_hero(k.killed_npc.spawning_hero.name, k.time_point, dying_side)

                unique_tuple = (k.round_id, k.time_point, k.killing_player_id, dying_player.id)
                if False and unique_tuple in unique_set:
                    print(kill_feed_events)
                    print(k)
                    raise(CommandError)
                unique_set.add(unique_tuple)

                if not assists:
                    kill_feed_events.append(
                        models.KillFeedEvent(time_point=k.time_point, round=k.round,
                                             killing_player=k.killing_player,
                                             dying_player=dying_player,
                                             dying_npc=k.killed_npc,
                                             ability=k.ability))
                else:
                    m = models.KillFeedEvent.objects.create(time_point=k.time_point, round=k.round,
                                                            killing_player=k.killing_player,
                                                            dying_player=dying_player,
                                                            dying_npc=k.killed_npc,
                                                            ability=k.ability)
                    for assisting_player in assists:
                        m.assisting_players.add(assisting_player)
            deaths = r.get_nonkill_npcdeaths()
            for d in deaths:
                dying_side = 'left' if d.side == 'L' else 'right'
                dying_player = r.get_player_of_hero(d.npc.spawning_hero.name, d.time_point, dying_side)
                if dying_player is None:
                    continue
                    print(d, dying_side)
                unique_tuple = (d.round_id, d.time_point, None, dying_player.id)
                if False and unique_tuple in unique_set:
                    print(kill_feed_events)
                    print(d)
                    print(dying_player)
                    raise(CommandError)
                unique_set.add(unique_tuple)

                kill_feed_events.append(models.KillFeedEvent(time_point=d.time_point, round=d.round,
                                                             dying_npc=d.npc,
                                                             dying_player=dying_player))
            denials = r.ultdenial_set.all()
            for d in denials:
                unique_tuple = (d.round_id, d.time_point, d.denying_player_id, d.denied_player_id)
                if False and unique_tuple in unique_set:
                    print(kill_feed_events)
                    print(d)
                    raise(CommandError)
                unique_set.add(unique_tuple)

                hero = d.denying_player.get_hero_at_timepoint(r, d.time_point)
                denying_ability = hero.abilities.get(type=models.Ability.DENYING_TYPE)
                kill_feed_events.append(
                    models.KillFeedEvent(time_point=d.time_point, round=d.round,
                                         killing_player=d.denying_player,
                                         ability=denying_ability,
                                         dying_player=d.denied_player,
                                         denied_ult=d.ability))
            revives = r.revive_set.all()
            for d in revives:
                unique_tuple = (d.round_id, d.time_point, d.reviving_player_id, d.revived_player_id)
                if False and unique_tuple in unique_set:
                    print(kill_feed_events)
                    print(d)
                    raise(CommandError)
                unique_set.add(unique_tuple)

                kill_feed_events.append(
                    models.KillFeedEvent(time_point=d.time_point, round=d.round,
                                         killing_player=d.reviving_player,
                                         ability=d.ability,
                                         dying_player=d.revived_player))
            models.KillFeedEvent.objects.bulk_create(kill_feed_events)
