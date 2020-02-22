from django import forms


class StartGame(forms.Form):
    # we set the maximum of 6 players because we're playing with only one deck
    player_count = forms.IntegerField(min_value=2, max_value=6)
