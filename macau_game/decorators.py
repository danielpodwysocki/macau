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
        player_seat_count = Seat.objects.filter(
            done=False, player=request.user).count()
        if player_seat_count == 0:
            return redirect('index')
        else:
            seat = Seat.objects.get(player=request.user)
            print(Seat.objects.filter(game=seat.game, done=False).count())
            if Seat.objects.filter(done=False, game=seat.game).count() < 2 and seat.game.full is True:
                print('xd')
                return redirect('index')

            return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
