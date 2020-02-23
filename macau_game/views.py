from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from macau_game import models, forms
from random import randrange
from macau_game import decorators
from random import choices, choice

# Create your views here.


@login_required
def index(request):  # TODO: this view lets you create or join a game
    u = request.user  # just for testing untill i make the index page

    context = {'f_start_game': forms.StartGame, 'f_join_game': forms.JoinGame}
    return render(request, 'macau/index.html', context)


@login_required
@decorators.not_in_game
def start_game(request):  # TODO: error messages (after error view is finished)
    '''
    this view creates a new game and its settings,
    assigns the player(the one who created it) to it, makes it either public or private, then redirects you to the game view itself
    '''

    if request.method != 'POST':
        return redirect('error')
    form = forms.StartGame(request.POST)
    if form.is_valid() is False:
        return redirect('error')

    player_count = form.cleaned_data['player_count']

    deck = list(range(1, 53))

    # remove "actionable" cards from the deck from which we pick the top card
    banned = [1, 2, 3, 4, 11, 12, 13]
    for i in range(4):
        for b in banned:
            deck.remove(13*i+b)

    game = models.Game(player_count=player_count, is_finished=False,
                       starting_player=randrange(1, player_count+1), top_card=choice(deck), full=False)
    game.save()
    seat = models.Seat(player=request.user, game=game,
                       seat_number=0, done=False)
    seat.save()
    return(redirect('game'))


@login_required
@decorators.not_in_game
# TODO: error messages (after error view is finished)
def join_game(request):
    if request.method != 'POST':
        return redirect('error')
    form = forms.JoinGame(request.POST)
    if(form.is_valid()) is False:
        return redirect('error')
    game = models.Game.objects.get(pk=form.cleaned_data['game_id'])
    seat_count = models.Seat.objects.filter(game=game).count()
    if seat_count >= game.player_count:
        return redirect('error')
    seat = models.Seat(player=request.user, game=game,
                       seat_number=seat_count, done=False)
    seat.save()
    if seat_count+1 == game.player_count:
        game.full = True
        game.save()
        # 'deal out' the cards to players:
        deck = list(range(1, 53))
        deck.remove(game.top_card)
        seats = list(models.Seat.objects.filter(game=game))
        for s in seats:
            hand = choices(deck, k=5)
            for card in hand:
                deck.remove(card)
                c = models.Card(game=game, card=card, player=s.player)
                c.save()

    return redirect('game')


@login_required
def game(requst):  # TODO the game view
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
