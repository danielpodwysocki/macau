from macau_game import models


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
