from macau_game.models import Seat
from django.shortcuts import redirect


# check if player is already in game, if he is redirect him to it
def not_in_game(function):
    def wrap(request, *args, **kwargs):
        last_seat = Seat.objects.filter(
            done=False, player=request.user).count()
        if last_seat != 0:
            return redirect('game')
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def in_game(function):
    '''
    if the player is not in an active game, redirect to index
    '''
    def wrap(request, *args, **kwargs):
        last_seat = Seat.objects.filter(
            done=False, player=request.user).count()
        if last_seat == 0:
            return redirect('game')
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
