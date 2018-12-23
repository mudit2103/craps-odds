"""This script is written to figure out what the best way to play
craps at a casino is."""
from collections import namedtuple
from random import randint
from enum import Enum

class GameStates(Enum):
	ON = 1
	OFF = 2

class Bets(Enum):
	PASS = 1
	DONTPASS = 2

class Game():
	def __init__(self, bets, money, rounds):
		self.state = GameStates.OFF
		self.point = None
		self.money = money
		self.rounds = rounds
		self.bets = bets

		# Ensure that only one of PASS and DONTPASS is in bets.
		assert not((Bets.PASS in bets) and (Bets.DONTPASS in bets))


multipliers = {Bets.PASS: 1, Bets.DONTPASS: 1}

STARTING_MONEY = 10000
GAME_STATE = GameStates.OFF
ROUNDS = 10000


def roll():
	"""Rolls two dice. Returns the result as a RolledDice NamedTuple"""
	d1 = randint(1, 6)
	d2 = randint(1, 6)
	summed = d1 + d2

	return summed

def init_game(bets=None, money=STARTING_MONEY, rounds=ROUNDS):
	"""Initializes a game instance.
	bets must be a dictionary mapping Bets enums to amounts.
	money must be an int, the starting money.
	rounds must be an int, the number of rounds to play.

	Returns an initialized game instance."""
	if bets is None:
		bets = {Bets.PASS: 10}

	game = Game(bets, money, rounds)
	return game

def sim_one(game):
	"""Simulates one round of the game."""
	result = roll()

	if game.state == GameStates.OFF:
		process_off(game, result)
	else:
		process_on(game, result)

	game.rounds -= 1

def win(game, bet):
	"""Checks to see if a particular bet was made in a game.
	If it was made, then acts on winning this bet."""
	if bet in game.bets:
		game.money += multipliers[bet] * game.bets[bet]

def lose(game, bet):
	"""Checks to see if a particualr bet was game in a game.
	If it was made, then acts of losing the bet."""
	if bet in game.bets:
		game.money -= multipliers[bet] * game.bets[bet]

def process_off(game, result):
	"""Processes a single iteration of the game when the
	game is initially in the off state.

	The rules of craps dictate that if the roll was a 
	7 or an 11, the pass line wins, and the dont pass line loses.

	If the roll was a 2, 3, 12, then the dont pass line wins, and 
	the pass line loses.

	If the roll was anything else, then a point is established,
	and the game is switched to on.
	"""
	if result in [7, 11]:
		win(game, Bets.PASS)
		lose(game, Bets.DONTPASS)

	elif result in [2, 3, 12]:
		lose(game, Bets.PASS)
		win(game, Bets.DONTPASS)

	else:
		game.point = result
		game.state = GameStates.ON


def process_on(game, result):
	# If the game is on, there should be a point established.
	assert game.point is not None  

	if result == 7:
		lose(game, Bets.PASS)
		win(game, Bets.DONTPASS)

	elif result == game.point:
		win(game, Bets.PASS)
		lose(game, Bets.DONTPASS)
		

def sim_all(game):
	while game.rounds != 0:
		sim_one(game)


def compute_average():
	results = []
	for i in range(100):
		game = init_game()
		sim_all(game)
		results.append(game.money)

	for i in results:
		print(i)
	print("The average is ", sum(results)/len(results))

compute_average()



























