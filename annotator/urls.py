from django.conf.urls import url, include
from django.contrib.staticfiles.views import serve
from django.views.generic import RedirectView
from . import views
from rest_framework import routers
from . import api

app_name = 'annotator'

api_router = routers.DefaultRouter()
api_router.register(r'heroes', api.HeroViewSet, base_name='heroes')
api_router.register(r'maps', api.MapViewSet, base_name='maps')
api_router.register(r'npcs', api.NPCViewSet, base_name='npcs')
api_router.register(r'events', api.EventViewSet, base_name='events')
api_router.register(r'games', api.GameViewSet, base_name='games')
api_router.register(r'players', api.PlayerViewSet, base_name='players')
api_router.register(r'teams', api.TeamViewSet, base_name='teams')
api_router.register(r'team_colors', api.TeamColorViewSet, base_name='team_colors')
api_router.register(r'sides', api.SideViewSet, base_name='sides')
api_router.register(r'matches', api.MatchViewSet, base_name='matches')
api_router.register(r'rounds', api.RoundViewSet, base_name='rounds')
api_router.register(r'switches', api.SwitchViewSet, base_name='switches')
api_router.register(r'deaths', api.DeathViewSet, base_name='deaths')
api_router.register(r'unpauses', api.UnpauseViewSet, base_name='unpauses')
api_router.register(r'ultuses', api.UltUseViewSet, base_name='ultuses')
api_router.register(r'ultgains', api.UltGainViewSet, base_name='ultgains')
api_router.register(r'revives', api.ReviveViewSet, base_name='revives')
api_router.register(r'pointgains', api.PointGainViewSet, base_name='pointgains')
api_router.register(r'pointflips', api.PointFlipViewSet, base_name='pointflips')
api_router.register(r'pauses', api.PauseViewSet, base_name='pauses')
api_router.register(r'npcdeaths', api.NPCDeathViewSet, base_name='switches')
api_router.register(r'kills', api.KillViewSet, base_name='kill')
api_router.register(r'killnpcs', api.KillNPCViewSet, base_name='killnpcs')
api_router.register(r'replaystarts', api.ReplayStartViewSet, base_name='replaystarts')
api_router.register(r'replayends', api.ReplayEndViewSet, base_name='replayends')
api_router.register(r'overtimestarts', api.OvertimeStartViewSet, base_name='overtimestarts')

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # url(r'^import_annotations/$', views.import_annotations, name='import_annotations'),
    url('^api/', include(api_router.urls)),
]
