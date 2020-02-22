from django import forms
from macau_game import models
from django.db.models import F


class StartGame(forms.Form):
    # we set the maximum of 6 players because we're playing with only one deck
    player_count = forms.IntegerField(min_value=2, max_value=6)


class JoinGame(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = models.Game.objects.filter(
            full=False).values_list('pk', flat=True)
        choices = list(choices)
        choicez = [(i, i) for i in choices]
        self.fields['game_id'] = forms.ChoiceField(
            choices=choicez)
