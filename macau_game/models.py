'''
    Models for the macau app
'''
from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    '''
        Represents a game and gives us info about it: is it finished and how many players are in it
    '''
    player_count = models.PositiveSmallIntegerField()
    top_card = models.SmallIntegerField()
    is_finished = models.BooleanField()
    # number of the starting player, assuming they move in a clockwise fashion and are sorted by id
    starting_player = models.SmallIntegerField()


class Move(models.Model):
    '''
        A single move: we know which player made the move and what in what game it happened
        We figure out the sequence of moves simply by sorting by ids
    '''
    player = models.ForeignKey(to=User, on_delete=models.CASCADE)
    game = models.ForeignKey(to=Game, on_delete=models.CASCADE)


class Throw(models.Model):
    '''
        A single throw (a move can be more than one throw)
        We figure out the sequence of throws simply by sorting by ids

    '''
    move = models.ForeignKey(to=Move, on_delete=models.CASCADE)
    # cards are represented as value (ace=1, king=13) + suit*13(Clubs=0,Hearts=1,Spades=2,Diamonds=3)
    card = models.SmallIntegerField()


class Card(models.Model):
    '''
        the purpose of this model is to connect the player's hand with the game.
        those models get deleted as the cards are thrown
        the reason for not doing this in a session is the possibility of "correspondance" play
    '''
    game = models.ForeignKey(to=Game, on_delete=models.CASCADE)
    player = models.ForeignKey(to=User, on_delete=models.CASCADE)
    # cards are represented as value (ace=1, king=13) + suit*13(Clubs=0,Hearts=1,Spades=2,Diamonds=3)
    card = models.SmallIntegerField()


class Seat(models.Model):
    '''
        ties player to game, tells us what seat he's "in" and if he's finished
    '''
    game = models.ForeignKey(to=Game, on_delete=models.CASCADE)
    player = models.ForeignKey(to=User, on_delete=models.CASCADE)
    seat_number = models.SmallIntegerField()
    done = models.BooleanField()
