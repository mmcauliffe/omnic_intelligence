from django.conf.urls import url, include
from . import views
from rest_framework import routers
from .api import EventViewSet, GameViewSet, MatchViewSet, RoundViewSet, SwitchViewSet, DeathViewSet, UnpauseViewSet, \
    UltUseViewSet, UltGainViewSet, ReviveViewSet, PointGainViewSet, PointFlipViewSet, PauseViewSet, NPCDeathViewSet, \
    KillViewSet, KillNPCViewSet

app_name = 'annotator'

event_router = routers.DefaultRouter()
event_router.register(r'events', EventViewSet, base_name='events')
event_router.register(r'games', GameViewSet, base_name='games')
event_router.register(r'matches', MatchViewSet, base_name='matches')
event_router.register(r'rounds', RoundViewSet, base_name='rounds')
event_router.register(r'switches', SwitchViewSet, base_name='switches')
event_router.register(r'deaths', DeathViewSet, base_name='deaths')
event_router.register(r'unpauses', UnpauseViewSet, base_name='unpauses')
event_router.register(r'ultuses', UltUseViewSet, base_name='ultuses')
event_router.register(r'ultgains', UltGainViewSet, base_name='ultgains')
event_router.register(r'revives', ReviveViewSet, base_name='revives')
event_router.register(r'pointgains', PointGainViewSet, base_name='pointgains')
event_router.register(r'pointflips', PointFlipViewSet, base_name='pointflips')
event_router.register(r'pauses', PauseViewSet, base_name='pauses')
event_router.register(r'npcdeaths', NPCDeathViewSet, base_name='switches')
event_router.register(r'kills', KillViewSet, base_name='kill')
event_router.register(r'killnpcs', KillNPCViewSet, base_name='killnpcs')

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # url(r'^import_annotations/$', views.import_annotations, name='import_annotations'),
    # url(r'match/(?P<match_id>\d+)/', views.MatchInspector.as_view(), name='inspect_match'),
    # url(r'game/(?P<game_id>\d+)/', views.GameInspector.as_view(), name='inspect_game'),
    # url(r'round/(?P<round_id>\d+)/', views.RoundInspector.as_view(), name='inspect_round'),
    # url(r'update_teams/', views.update_team, name='update_team'),
    # url(r'delete_event/', views.delete_event, name='delete_event'),
    # url(r'get_abilities/', views.get_current_hero_abilities, name='get_abilities'),
    # url(r'^crud/switch/?$', views.SwitchCRUDView.as_view(), name='switch_crud_view'),
    # url(r'^rounds/(?P<pk>\d+)/posts$', SwitchList.as_view(), name='switch-list'),
    # url(r'^rounds/(?P<pk>\d+)$', RoundDetail.as_view(), name='round-detail'),
    # url(r'^rounds/$', RoundList.as_view(), name='round-list'),
    # url(r'^matches/(?P<pk>\d+)$', MatchDetail.as_view(), name='match-detail'),
    # url(r'^matches/$', MatchList.as_view(), name='match-list')
    # url('^events/', views.events_index,name='events_view'),
    url('^api/', include(event_router.urls)),
]
