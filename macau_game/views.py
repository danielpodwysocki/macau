from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from macau_game import models, forms, game_funcs
from random import randrange
from macau_game import decorators
from random import sample, choices, choice
from math import ceil
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
                       starting_player=randrange(0, player_count), top_card=choice(deck), full=False)
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
        print(game.top_card)
        deck.remove(game.top_card)
        seats = list(models.Seat.objects.filter(game=game))
        for s in seats:
            hand = sample(deck, k=5)
            print("hand:" + str(hand))
            print("deck:" + str(deck))
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
@decorators.in_game
def move(request):
    # we create a new move model after each move, because we want a to have a history of all moves, kind of like on lichess.org
    # also end the game if the move is the last one (defined by there being one player left in the game)
    # TODO: create responses other than 'ok' and 'bad_throw'
    # TODO: implement 'special' mechanics
    # TODO: check if it's the user's turn
    response = {}
    response['return'] = 'ok'
    try:

        # check request method and parameters
        if request.method != 'POST' or request.POST.get('throws') == None:
            raise Exception('bad_request')

        throws = json.loads(request.POST.get('throws'))
        user = request.user
        seat = models.Seat.objects.get(
            done=False, player=request.user)
        game = seat.game
        top_card = models.Throw.objects.filter(
            move__game=game).last()  # get the top card
        # we recognize the current battle state based on the Game.special_state, so we don't need to have a complete history of throws

        if top_card == None:
            # if it's the first move of the game, get the top card from the Game model
            top_card = game.top_card

        # check if it's this user's turn
        print(game_funcs.active_seat(game).seat_number)
        if game_funcs.active_seat(game) != seat:
            raise Exception("wrong_turn")
        if throws[0] == 'draw':  # check if the user is drawing cards instead of playing them

            # TODO: Prepare for a case in which all the cards had been drawn and there's no more cards in the deck
            # (maybe a 'debt' system of drawing cards as soon as they become available?)
            to_draw = 1
            if game.special_state < 0 and game.special_state >= -13:
                to_draw = abs(game.special_state)
            player_cards = models.Card.objects.filter(
                game=game).values_list('card', flat=True)  # card values to be excluded from drawing, because they belong to players

            # removing cards already in play
            deck = list(range(1, 53))
            for c in player_cards:
                deck.remove(c)
            deck.remove(game.top_card)

            drawn_cards = sample(deck, k=to_draw)
            for card in drawn_cards:
                c = models.Card(game=game, card=card, player=user)
                c.save()

            # create a move, don't tie any cards to it (since we didn't place any)
            move = models.Move(player=user, game=game)
            move.save()

            response['return'] = 'ok'
            return JsonResponse(response)

        # check if the submitted cards are in the user's hand
        for t in throws:
            card_count = models.Card.objects.filter(
                player=user, card=t).count()
            if card_count == 0:
                raise Exception('bad_throw')

        # check if all of the cards in the throw have the same value, otherwise throw an Exception
        sample = throws[0]
        sample_suit = ceil(throws[0]/13)
        sample_value = sample - (sample_suit-1) * 13
        # since this card skips all checks we'll make a variable for it to avoid complex if statements
        queen_of_spades = False
        for t in throws:
            t_suit = ceil(t/13)
            t_value = t - (t_suit-1)*13
            if t_value != sample_value:
                raise Exception('bad_throw')
            if t_suit == 2 and t_value == 12:
                queen_of_spades = True
        # check if there's a battle and if so if the cards addresses that
        # TODO: figure out the ruleset we want to go by and implement that one (right now it's any-on-any battle, there's also the hungarian variation)
        if game.special_state > 0:
            battle_values = [2, 3, 13]
            # also check for the queen of spades
            if sample_value not in battle_values or sample_value != 12 and sample_suit != 2:
                raise Exception('bad_throw')

        # last card thrown, aka the top card of the game
        top_card = game_funcs.get_top_card(game)
        top_card_suit = ceil(top_card/13)
        top_card_value = top_card - (top_card_suit-1) * 13
        print(top_card)
        # check if the throws[0] matches the top card of the game, or if it's not a queen of spades (goes on top of anything)
        if (sample_value == top_card_value or sample_suit == top_card_suit) is False and queen_of_spades is False:
            print('xd')
            raise Exception('bad_throw')

        # Next two ifs check if there is a pending demand and if the bottom card of the throw addresses that
        # bottom card meaning throws[0] (represented by sample_value and sample_suit),
        # as it is the first card to be thrown and ends up on top of the card that's currently on top of the pile

        # check for a demand indicating the value of a card and if response matches the demand,
        # eventually if the demand can still be change (if a jack is on top and the user has thrown a jack)
        if game.special_state < 0 and game.special_state >= -13 and queen_of_spades is False:
            demand_value = game.special_state*(-1)

            if sample_value == demand_value:
                pass
            elif top_card_value == 11 == sample_value:
                pass
            else:
                raise Exception('bad_throw')

        # check for a demand indicating the suit of a thrown card and if the response matches the demand or
        # can be changed by throwing an ace (while an ace is still on top)
        if game.special_state < -13 and queen_of_spades is False:
            # adjusting for the value scheme for the demand outlined in models.Game
            demand_suit = game.special_state * (-1) / 10 - 2

            if demand_suit == sample_suit:
                pass
            elif top_card_value == 1 == sample_value:
                pass
            else:
                raise Exception('bad_throw')

        # create the move object, delete cards from the player's hand, create the throw model
        move = models.Move(player=user, game=game)
        move.save()
        for c in throws:  # c representing the value of a card
            card = models.Card.objects.get(game=game, player=user, card=c)
            card.delete()
            throw = models.Throw(move=move, card=c)
            throw.save()
        # if the user's hand is now empty, change the Seat.done to True
        cards_left = models.Card.objects.filter(
            game=game, player=user).count()
        if cards_left == 0:
            seat.done = True
            seat.save()
            # now check if there's more than 1 player left, if not end the game
            seat_count = models.Seat.objects.filter(
                game=game, done=False).count()
            if seat_count <= 0:
                game.is_finished = True
                game.save()

        # return 'ok'
        return JsonResponse(response)

    except Exception as e:
        response['return'] = e.args
        print(e.args)
        return JsonResponse(response)


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
        active_player - a number signyfing which players turn it is
        in the below comments the "user" refers to the one that made the request for the json,
        players are the rest of the people playing
        move_count - it lets us know if the game has advanced

    '''
    user = request.user
    seat = models.Seat.objects.get(
        done=False, player=request.user)
    game = seat.game
    last_throw = models.Throw.objects.filter(move__game=game).last()
    move_count = models.Move.objects.filter(game=game).count()

    response = {}
    response['player_count'] = game.player_count
    response['hands'] = []
    response['full'] = game.full
    response['position'] = seat.seat_number
    response['top_cards'] = ''
    response['move_count'] = move_count
# TODO: refactor the next if statement + the last_throw above using game_funcs, they're doing basically the same things
    if last_throw != None:
        response['active_player'] = game_funcs.active_seat(game).seat_number
        response['top_cards'] = last_throw.card
    else:
        response['active_player'] = game.starting_player
        response['top_cards'] = game.top_card

    if game.full:
        # flat=True for values instead of one-tuples
        user_hand = list(models.Card.objects.filter(
            player=user).values_list('card', flat=True))
        # we append the amount of cards each has (except for the user, we append his hand)
        for i in range(game.player_count):
            if i == seat.seat_number:
                response['hands'].append(user_hand)
            else:
                player = models.Seat.objects.get(
                    game=game, seat_number=i).player
                response['hands'].append(
                    models.Card.objects.filter(game=game, player=player).count())

    return JsonResponse(response)


def error(request):  # TODO: returns an error message explaining what went wrong
    '''
    The error view
    '''
    return HttpResponse('error')
