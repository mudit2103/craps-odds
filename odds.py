"""This script is written to figure out what the best way to play
craps at a casino is."""
from collections import namedtuple
from random import randint
from enum import Enum
import logging
from multiprocessing import Pool

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class GameStates(Enum):
	ON = 1  # When the point has been established
	OFF = 2

class Bets(Enum):
	PASS = 1
	DONTPASS = 2

	_4 = 4
	_5 = 5
	_6 = 6
	_8 = 8
	_9 = 9
	_10 = 10


class Game():
	def __init__(self, bets, money, rounds):
		self.state = GameStates.OFF
		self.point = None
		self.money = money
		self.rounds = rounds
		self.bets = bets
		self.point_rounds = 0
		self.old_bets = None

		# Ensure that only one of PASS and DONTPASS is in bets.
		assert not((Bets.PASS in bets) and (Bets.DONTPASS in bets))


multipliers = {
	Bets.PASS: 1, Bets.DONTPASS: 1,
	Bets._4: 9/5, Bets._10: 9/5,
	Bets._5: 7/5, Bets._9: 7/5,
	Bets._6: 7/6, Bets._8: 7/6
}

STARTING_MONEY = 10000
GAME_STATE = GameStates.OFF
ROUNDS = 10000
CACHE_THRESHOLD = 5
CACHED = False

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

def win(game, bet):
	"""Checks to see if a particular bet was made in a game.
	If it was made, then acts on winning this bet."""
	if bet in game.bets:
		logging.debug("Won on {}. Money was {}.".format(bet, game.money))
		game.money += multipliers[bet] * game.bets[bet]
		logging.debug("Money is now {}".format(game.money))

def lose(game, bet):
	"""Checks to see if a particualr bet was game in a game.
	If it was made, then acts of losing the bet."""
	if bet in game.bets:
		logging.debug("Lost on {}. Money was {}.".format(bet, game.money))
		game.money -= multipliers[bet] * game.bets[bet]
		logging.debug("Money is now {}".format(game.money))

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
		logging.debug("Rolled a natural win!")
		win(game, Bets.PASS)
		lose(game, Bets.DONTPASS)

	elif result in [2, 3, 12]:
		logging.debug("Craps on off.")
		lose(game, Bets.PASS)
		win(game, Bets.DONTPASS)

	else:
		logging.debug("Point established at {}".format(str(result)))
		game.point = result
		game.state = GameStates.ON

def process_on(game, result):
	"""Processes one iteration of the game when the game was on to
	begin with

	Craps rules say the following:
	1. If a second is rolled, it's craps. The game moves to off state,
	and all bets are lost. Pass line loses, don't pass line wins.

	2. If the point is rolled, passline wins, don't pass line loses,
	and game is switched to off. 

	3. For 4, 5, 6, 8, 9, 10, we pay off the house bets.
	"""

	# If the game is on, there should be a point established.
	assert game.point is not None  

	if result == 7:
		logging.debug("Oh craps...")
		lose(game, Bets.PASS)
		win(game, Bets.DONTPASS)
		for bet in [Bets._4, Bets._5, Bets._6, Bets._8, Bets._9, Bets._10]:
			lose(game, bet)

		finish_round(game)

	elif result in [4, 5, 6, 8, 9, 10]:
		idx = [4, 5, 6, 8, 9, 10].index(result)
		bets = [Bets._4, Bets._5, Bets._6, Bets._8, Bets._9, Bets._10]
		bet = bets[idx]
		win(game, bet)
		game.point_rounds += 1

		if game.point_rounds > CACHE_THRESHOLD and not CACHED:
			cache_and_clear_house_bets(game)


	if result == game.point:
		logging.debug("Point")
		win(game, Bets.PASS)
		lose(game, Bets.DONTPASS)
		finish_round(game)

def finish_round(game):
	game.state = GameStates.OFF
	game.point_rounds = 0
	game.rounds -= 1

	logging.debug("{} rounds left".format(game.rounds))

	uncache_bets(game)

def sim_one(game):
	"""Simulates one round of the game."""
	result = roll()
	logging.debug("Rolled a {}".format(str(result)))
	logging.debug("Game state was {}".format(str(game.state)))

	if game.state == GameStates.OFF:
		process_off(game, result)
	else:
		process_on(game, result)

	logging.debug("\n")

def sim_all(game):
	while game.rounds != 0:
		sim_one(game)

def compute_average():
	results = []
	bets = {
			Bets.PASS: 10, 
			Bets._4: 5, Bets._10: 5,
			Bets._5: 5, Bets._9: 5,
			Bets._6: 6, Bets._8: 6
		}


	for i in range(1):
		game = init_game(bets, 10000, 100)
		sim_all(game)
		results.append(game.money)

	for i in results:
		print(i)
	print("The average is ", sum(results)/len(results))

def cache_and_clear_house_bets(game):
	"""Function as a catchall to try special tricks to make more money."""
	global CACHED
	print("BETS HAVE BEEN CACHED")
	CACHED = True
	game.old_bets = game.bets
	game.bets = {Bets.PASS: game.old_bets[Bets.PASS]}

def uncache_bets(game):
	global CACHED
	CACHED = False
	if game.old_bets is not None:
		game.bets = game.old_bets

compute_average()



























