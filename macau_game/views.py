from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):#TODO: this view lets you create or join a game
    return HttpResponse('index')

def start_game(request): #TODO: this view creates a new game and its settings,
    #assigns the player(the one who created it) to it, makes it either public or private, then redirects you to the game view itself
    return HttpResponse('start game')

def join_game(request): #TODO
    return HttpResponse('join_game')

def game(requst): #TODO the game view
    return HttpResponse('game')

def move(request): #TODO: submit a move, evaluate if it's legal, if it is create and/or update consequential models 
    # we create a new move model after each move, because we want a to have a history of all moves, kind of like on lichess.org
    # also end the game if the move is the last one
    return HttpResponse('move') 

def state(request): #TODO: return a json with the current state of the game, containing special conditions, etc.
    return HttpResponse('state')
