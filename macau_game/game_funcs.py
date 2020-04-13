from macau_game import models
from random import sample


def active_seat(game):
    '''
    takes a Game object as an argument,
    returns the Seat object assigned to the active player
    '''
    last_move = models.Move.objects.filter(game=game).last()
    if last_move == None:
        return models.Seat.objects.get(game=game, seat_number=game.starting_player)
    last_player = last_move.player
    last_seat = models.Seat.objects.get(game=game, player=last_player)
    seats = list(models.Seat.objects.filter(
        game=game).order_by('-pk'))
    return_next = False  # we turn that to true
    while True:
        for s in seats:
            if return_next and s.done is False:
                return s
            if s == last_seat:
                return_next = True


def get_top_card(game):
    last_throw = models.Throw.objects.filter(move__game=game).last()
    if last_throw != None:
        return last_throw.card
    else:
        return game.top_card


def draw(game, user):

    # TODO: Prepare for a case in which all the cards had been drawn and there's no more cards in the deck
    # (maybe a 'debt' system of drawing cards as soon as they become available?)
    to_draw = 1
    if game.special_state > 0:
        to_draw = game.special_state
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
    # reset any battle states, advance demand state timers
    if game.special_state > 0:
        game.special_state = 0
        game.demand_time = 0

    if game.demand_time > 0:
        game.demand_time -= 1

    if game.demand_time == 0 and game.special_state < 0:
        game.special_state = 0

    game.save()
