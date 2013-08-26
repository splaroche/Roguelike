########################################################
# Welcome to my Roguelike!  The base code is modified
# from the libtcod python library tutorial, but it has
# been adapted to use an object-oriented approach.
########################################################

from game import Game

# start the game
g = Game()
g.game_state = 'playing'
g.main_menu()