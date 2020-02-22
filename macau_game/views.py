from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from macau_game import models, forms
from random import randrange
# Create your views here.


@login_required
def index(request):  # TODO: this view lets you create or join a game
    u = request.user  # just for testing untill i make the index page

    context = {'f_start_game': forms.StartGame}
    return render(request, 'macau/index.html', context)


@login_required
def start_game(request):  # TODO: error messages (after error view is finished)
    '''
    this view creates a new game and its settings,
    assigns the player(the one who created it) to it, makes it either public or private, then redirects you to the game view itself
    '''
    last_seat = models.Seat.objects.filter(
        done=False, player=request.user).count()
    if last_seat != 0:
        return(redirect('game'))

    if request.method != 'POST':
        return redirect('error')
    form = forms.StartGame(request.POST)
    if form.is_valid() is False:
        return redirect('error')

    player_count = form.cleaned_data['player_count']
    game = models.Game(player_count=player_count, is_finished=False,
                       starting_player=randrange(1, player_count+1), top_card=randrange(1, 53))
    game.save()
    seat = models.Seat(player=request.user, game=game,
                       seat_number=0, done=False)
    seat.save()
    return(redirect('game'))


@login_required
def join_game(request):  # TODO

    return HttpResponse('join_game')


@login_required
def game(requst):  # TODO the game view
    last_move = move.get(player=request.user).order_by(
        'pk')  # last move made by this player
    return HttpResponse('game')


@login_required
def move(request):  # TODO: submit a move, evaluate if it's legal, if it is create and/or update consequential models
    # we create a new move model after each move, because we want a to have a history of all moves, kind of like on lichess.org
    # also end the game if the move is the last one
    return HttpResponse('move')


# TODO: return a json with the current state of the game, containing special conditions, etc.
@login_required
def state(request):
    return HttpResponse('state')


def error(request):  # TODO: returns an error message explaining what went wrong
    '''
    The error view
    '''
    return HttpResponse('error')
