from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from macau_game import models, forms
from random import randrange
from macau_game import decorators
from random import choices, choice
import json

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
@decorators.in_game
def game(request):  # TODO the game view
    return render(request, 'macau/game.html')


@login_required
def move(request):  # TODO: submit a move, evaluate if it's legal, if it is create and/or update consequential models
    # we create a new move model after each move, because we want a to have a history of all moves, kind of like on lichess.org
    # also end the game if the move is the last one
    return HttpResponse('move')


# TODO: return a json with the current state of the game, containing special macau game conditions(battle, demand, etc) and other info.
@login_required
@decorators.in_game
def state(request):
    '''
        returns a json with the current state of the game, represented by:
        player_count - amount of players
        hands[] - an array that has a number of cards for each hand, except for the player making the request.
        instead of his no. of cards we have a nested array containg his exact hand, so it can be displayed.
        0 represents a player that has either resigned, won/finished (got rid of all his cards) or an empty seat yet to be joined
        full - tells us if we're still waiting for more players
        position - our player's position at the table (his seat no., counting from 0) - this is needed, since from the player's view
        he always sits at the "bottom" of the "table" (viewport)
        top_cards - an arr containg all the already thrown cards (TODO:)that haven't yet been reshuffled into the deck 

        in the below comments the "user" refers to the one that made the request for the json,
        players are the rest of the people playing
    '''
    user = request.user
    seat = models.Seat.objects.get(
        done=False, player=request.user)
    game = seat.game
    throws = list(models.Throw.objects.filter(move__game=game).order_by(
        '-pk')[10:].values_list('card', flat=True))

    response = {}
    response['player_count'] = game.player_count
    response['hands'] = []
    response['full'] = game.full
    response['position'] = seat.seat_number
    response['top_cards'] = throws

    if game.full:
        # flat=True for values instead of one-tuples
        user_hand = list(models.Card.objects.filter(
            player=user).values_list('card', flat=True))
        # we append the amount of cards each has (except for the user, we append his hand)
        for i in range(game.player_count):
            if i == seat.seat_number:
                response['hands'].append(user_hand)

            player = models.Seat.objects.get(game=game, seat_number=i).player
            response['hands'].append(
                models.Card.objects.filter(game=game, player=player).count())

    return JsonResponse(response)


def error(request):  # TODO: returns an error message explaining what went wrong
    '''
    The error view
    '''
    return HttpResponse('error')
