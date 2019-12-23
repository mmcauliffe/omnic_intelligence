"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers

from .api.views import index_view
from .api import views as api

api_router = routers.DefaultRouter()


# Admin

api_router.register(r'users', api.UserViewSet, base_name='users')

# Overwatch specific

api_router.register(r'heroes', api.HeroViewSet, base_name='heroes')
api_router.register(r'train_stats', api.TrainStatsViewSet, base_name='train_stats')
api_router.register(r'train_info', api.TrainInfoViewSet, base_name='train_info')
api_router.register(r'status_effect_choices', api.StatusEffectChoiceViewSet, base_name='status_effect_choices')
api_router.register(r'hero_summary', api.HeroSummaryViewSet, base_name='hero_summary')
api_router.register(r'abilities', api.AbilityViewSet, base_name='abilities')
api_router.register(r'maps', api.MapViewSet, base_name='maps')
api_router.register(r'npcs', api.NPCViewSet, base_name='npcs')
api_router.register(r'team_colors', api.TeamColorViewSet, base_name='team_colors')
api_router.register(r'map_modes', api.MapModeViewSet, base_name='map_modes')
api_router.register(r'sides', api.SideViewSet, base_name='sides')
api_router.register(r'submaps', api.SubmapViewSet, base_name='submaps')

# Recording
api_router.register(r'annotation_source_choices', api.AnnotationChoiceViewSet, base_name='annotation_source_choices')
api_router.register(r'spectator_mode_choices', api.SpectatorModeViewSet, base_name='spectator_mode_choices')
api_router.register(r'film_format_choices', api.FilmFormatViewSet, base_name='film_format_choices')
api_router.register(r'vod_status_choices', api.VodStatusChoiceViewSet, base_name='vod_status_choices')
api_router.register(r'vod_type_choices', api.VodTypeChoiceViewSet, base_name='vod_type_choices')
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
api_router.register(r'vods', api.VodViewSet, base_name='vods')
api_router.register(r'train_rounds', api.TrainRoundViewSet, base_name='train_rounds')
api_router.register(r'example_rounds', api.ExampleRoundViewSet, base_name='example_rounds')
api_router.register(r'train_rounds_plus', api.TrainRoundPlusViewSet, base_name='train_rounds_plus')
api_router.register(r'annotate_rounds', api.AnnotateRoundViewSet, base_name='annotate_rounds')
api_router.register(r'round_status', api.RoundStatusViewSet, base_name='round_status')
api_router.register(r'possible_denies', api.PossibleDenySearchViewSet, base_name='possible_denies')
api_router.register(r'possible_errors', api.GameParsingErrorViewSet, base_name='possible_errors')
api_router.register(r'vod_status', api.VodStatusViewSet, base_name='vod_status')

api_router.register(r'hero_picks', api.HeroPickViewSet, base_name='hero_picks')

api_router.register(r'ultimates', api.UltimateViewSet, base_name='ultimates')
api_router.register(r'status_effects', api.StatusEffectViewSet, base_name='status_effects')
api_router.register(r'kill_feed_events', api.KillFeedEventViewSet, base_name='kill_feed_events')

# Points

api_router.register(r'point_gains', api.PointGainViewSet, base_name='point_gains')
api_router.register(r'point_flips', api.PointFlipViewSet, base_name='point_flips')
api_router.register(r'overtimes', api.OvertimeViewSet, base_name='overtimes')

# Broadcast events

api_router.register(r'pauses', api.PauseViewSet, base_name='pauses')
api_router.register(r'replays', api.ReplayViewSet, base_name='replays')
api_router.register(r'smaller_windows', api.SmallerWindowViewSet, base_name='smaller_windows')
api_router.register(r'zooms', api.ZoomViewSet, base_name='zooms')

urlpatterns = [

    # http://localhost:8000/
    path('', index_view, name='index'),
    url(r'^api/rest-auth/', include('rest_auth.urls')),

    url(r'^api/rest-auth/registration/', include('rest_auth.registration.urls')),

    # http://localhost:8000/api/<router-viewsets>
    path('api/', include(api_router.urls)),

    path('api/grappelli/', include('grappelli.urls')),  # grappelli URLS
    # http://localhost:8000/api/admin/
    path('api/admin/', admin.site.urls),
]

#urlpatterns += [url(r'^api/silk/', include('silk.urls', namespace='silk'))]


