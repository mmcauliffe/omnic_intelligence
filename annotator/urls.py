from django.conf.urls import url, include
from django.contrib.staticfiles.views import serve
from django.views.generic import RedirectView
from . import views
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from . import api

app_name = 'annotator'

api_router = routers.DefaultRouter()
api_router.register(r'users', api.UserViewSet, base_name='users')
api_router.register(r'heroes', api.HeroViewSet, base_name='heroes')
api_router.register(r'hero_summary', api.HeroSummaryViewSet, base_name='hero_summary')
api_router.register(r'abilities', api.AbilityViewSet, base_name='abilities')
api_router.register(r'maps', api.MapViewSet, base_name='maps')
api_router.register(r'npcs', api.NPCViewSet, base_name='npcs')
api_router.register(r'events', api.EventViewSet, base_name='events')
api_router.register(r'games', api.GameViewSet, base_name='games')
api_router.register(r'players', api.PlayerViewSet, base_name='players')
api_router.register(r'teams', api.TeamViewSet, base_name='teams')
api_router.register(r'team_colors', api.TeamColorViewSet, base_name='team_colors')
api_router.register(r'spectator_modes', api.SpectatorModeViewSet, base_name='spectator_modes')
api_router.register(r'train_players', api.TrainPlayerViewSet, base_name='train_players')
api_router.register(r'film_formats', api.FilmFormatViewSet, base_name='film_formats')
api_router.register(r'sides', api.SideViewSet, base_name='sides')
api_router.register(r'map_modes', api.MapModeViewSet, base_name='map_modes')
api_router.register(r'annotationsources', api.AnnotationChoiceViewSet, base_name='annotationsources')
api_router.register(r'matches', api.MatchViewSet, base_name='matches')
api_router.register(r'rounds', api.RoundViewSet, base_name='rounds')
api_router.register(r'stream_channels', api.StreamChannelViewSet, base_name='stream_channels')
api_router.register(r'train_rounds', api.TrainRoundViewSet, base_name='train_rounds')
api_router.register(r'example_rounds', api.ExampleRoundViewSet, base_name='example_rounds')
api_router.register(r'train_rounds_plus', api.TrainRoundPlusViewSet, base_name='train_rounds_plus')
api_router.register(r'train_vods', api.TrainVodViewSet, base_name='train_vods')
api_router.register(r'annotate_rounds', api.AnnotateRoundViewSet, base_name='annotate_rounds')
api_router.register(r'annotate_vods', api.AnnotateVodViewSet, base_name='annotate_vods')
api_router.register(r'round_status', api.RoundStatusViewSet, base_name='round_status')
api_router.register(r'switches', api.SwitchViewSet, base_name='switches')
api_router.register(r'deaths', api.DeathViewSet, base_name='deaths')
api_router.register(r'unpauses', api.UnpauseViewSet, base_name='unpauses')
api_router.register(r'ult_uses', api.UltUseViewSet, base_name='ult_uses')
api_router.register(r'ult_gains', api.UltGainViewSet, base_name='ult_gains')
api_router.register(r'revives', api.ReviveViewSet, base_name='revives')
api_router.register(r'point_gains', api.PointGainViewSet, base_name='point_gains')
api_router.register(r'point_flips', api.PointFlipViewSet, base_name='point_flips')
api_router.register(r'pauses', api.PauseViewSet, base_name='pauses')
api_router.register(r'npc_deaths', api.NPCDeathViewSet, base_name='npc_deaths')
api_router.register(r'kills', api.KillViewSet, base_name='kill')
api_router.register(r'kill_npcs', api.KillNPCViewSet, base_name='kill_npcs')
api_router.register(r'replay_starts', api.ReplayStartViewSet, base_name='replay_starts')
api_router.register(r'replay_ends', api.ReplayEndViewSet, base_name='replay_ends')
api_router.register(r'overtime_starts', api.OvertimeStartViewSet, base_name='overtime_starts')
api_router.register(r'overtime_ends', api.OvertimeEndViewSet, base_name='overtime_ends')
api_router.register(r'smaller_window_starts', api.SmallerWindowStartViewSet, base_name='smaller_window_starts')
api_router.register(r'smaller_window_ends', api.SmallerWindowEndViewSet, base_name='smaller_window_ends')

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^import_annotations/$', views.import_annotations, name='import_annotations'),
    url('^api/', include(api_router.urls)),
    url(r'^export/(?P<round_id>\d+)/$', views.export_round, name='export'),
    url(r'check_channel/(?P<channel_id>\d+)/$', views.check_channel, name='check_channel')
]
