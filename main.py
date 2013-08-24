
import shelve
from base_character import Base_Character
import libtcodpy as libtcod


#game stat vars
from map import Map
from object import Object

game_state = 'playing'
player_action = None

####################################################################################################
# Random Choice Methods
####################################################################################################



####################################################################################################
# Movement Methods
####################################################################################################
from game import Game


g = Game()
g.game_state = 'playing'
g.main_menu()