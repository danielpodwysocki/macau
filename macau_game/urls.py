from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start_game', views.start_game, name='start_game'),
    path('join_game', views.join_game, name='join_game'),
    path('game', views.game, name='game'),
    path('move', views.move, name='move'),
    path('state', views.state, name='state'),
    path('error', views.error, name='error'),

]
