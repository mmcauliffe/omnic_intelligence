"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from .api.views import index_view
from .api import views as api

api_router = routers.DefaultRouter()


# Admin

api_router.register(r'users', api.UserViewSet, base_name='users')

# Overwatch specific

api_router.register(r'heroes', api.HeroViewSet, base_name='heroes')
api_router.register(r'hero_summary', api.HeroSummaryViewSet, base_name='hero_summary')
api_router.register(r'abilities', api.AbilityViewSet, base_name='abilities')
api_router.register(r'maps', api.MapViewSet, base_name='maps')
api_router.register(r'npcs', api.NPCViewSet, base_name='npcs')
api_router.register(r'team_colors', api.TeamColorViewSet, base_name='team_colors')
api_router.register(r'map_modes', api.MapModeViewSet, base_name='map_modes')
api_router.register(r'sides', api.SideViewSet, base_name='sides')

# Recording
api_router.register(r'annotation_sources', api.AnnotationChoiceViewSet, base_name='annotation_sources')
api_router.register(r'spectator_modes', api.SpectatorModeViewSet, base_name='spectator_modes')
api_router.register(r'film_formats', api.FilmFormatViewSet, base_name='film_formats')
api_router.register(r'stream_channels', api.StreamChannelViewSet, base_name='stream_channels')
api_router.register(r'train_vods', api.TrainVodViewSet, base_name='train_vods')
api_router.register(r'annotate_vods', api.AnnotateVodViewSet, base_name='annotate_vods')


# Teams
api_router.register(r'teams', api.TeamViewSet, base_name='teams')
api_router.register(r'players', api.PlayerViewSet, base_name='players')
api_router.register(r'train_players', api.TrainPlayerViewSet, base_name='train_players')


# Events
api_router.register(r'events', api.EventViewSet, base_name='events')
api_router.register(r'matches', api.MatchViewSet, base_name='matches')
api_router.register(r'games', api.GameViewSet, base_name='games')

# Rounds
api_router.register(r'rounds', api.RoundViewSet, base_name='rounds')
api_router.register(r'train_rounds', api.TrainRoundViewSet, base_name='train_rounds')
api_router.register(r'example_rounds', api.ExampleRoundViewSet, base_name='example_rounds')
api_router.register(r'train_rounds_plus', api.TrainRoundPlusViewSet, base_name='train_rounds_plus')
api_router.register(r'annotate_rounds', api.AnnotateRoundViewSet, base_name='annotate_rounds')
api_router.register(r'round_status', api.RoundStatusViewSet, base_name='round_status')
api_router.register(r'switches', api.SwitchViewSet, base_name='switches')
api_router.register(r'deaths', api.DeathViewSet, base_name='deaths')
api_router.register(r'ult_uses', api.UltUseViewSet, base_name='ult_uses')
api_router.register(r'ult_gains', api.UltGainViewSet, base_name='ult_gains')
api_router.register(r'revives', api.ReviveViewSet, base_name='revives')
api_router.register(r'point_gains', api.PointGainViewSet, base_name='point_gains')
api_router.register(r'point_flips', api.PointFlipViewSet, base_name='point_flips')
api_router.register(r'pauses', api.PauseViewSet, base_name='pauses')
api_router.register(r'npc_deaths', api.NPCDeathViewSet, base_name='npc_deaths')
api_router.register(r'kills', api.KillViewSet, base_name='kill')
api_router.register(r'kill_npcs', api.KillNPCViewSet, base_name='kill_npcs')
api_router.register(r'replays', api.ReplayViewSet, base_name='replays')
api_router.register(r'overtimes', api.OvertimeViewSet, base_name='overtimes')
api_router.register(r'smaller_windows', api.SmallerWindowViewSet, base_name='smaller_windows')

urlpatterns = [

    # http://localhost:8000/
    path('', index_view, name='index'),

    url(r'^api/rest-auth/', include('rest_auth.urls')),

    url(r'^api/rest-auth/registration/', include('rest_auth.registration.urls')),

    # http://localhost:8000/api/<router-viewsets>
    path('api/', include(api_router.urls)),

    # http://localhost:8000/api/admin/
    path('api/admin/', admin.site.urls),
]


