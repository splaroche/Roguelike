from map import GameMap
from objects import Object
from character_classes import BaseCharacterClass
from creatures import Player, Creature
from gui import Screen
import libtcodpy as libtcod
import shelve
from character_classes import *
class Game:
    def __init__(self):
        self.player = None
        self.player_action = None
        self.inventory = []
        self.game_state = None      
        self.map = GameMap()
        self.screen = Screen()
        self.map.screen = self.screen
    ####################################################################################################
    # Game Initialization Methods
    ####################################################################################################
    def new_game(self):

        #create object representing the player
        fighter_component = BaseCharacterClass(hp=100, defense=1, power=4)
        self.player = Player(0, 0, '@', 'player', libtcod.white, blocks=True, character_class=fighter_component)
        self.player.level = 1
        self.map.player = self.player
        self.map.objects.append(self.player)
       

        #set the dungeon level

        #generate map (at this point it's not drawn to the screen
        self.map.make()

        #generate the FOV
        self.map.initialize_fov()

        self.game_state = 'playing'
        self.inventory = []


        #a warm welcoming message!
        self.screen.message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', 'red')


   


    def play_game(self):

        self.player_action = None

        self.screen.mouse = libtcod.Mouse()
        self.screen.key = libtcod.Key()
        while not libtcod.console_is_window_closed():
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, self.screen.key, self.screen.mouse)
            self.screen.render_all(self.map)

            libtcod.console_flush()

            #check for levelups
            self.player.character_class.check_level_up(self.screen)

            #handle keys and exit game if needed
            for object in self.map.objects:
                object.clear(self.screen.con)
            self.player_action = self.screen.handle_keys(self.game_state, self.player, self.map.objects, self.map)

            #let monsters take their turn
            if self.game_state == 'playing' and self.player_action != 'didnt-take-turn':
                for object in self.map.objects:
                    if isinstance(object, Creature) and object.name != 'player':                        
                        object.ai.take_turn(self.player, self.screen)

            if self.player_action == 'exit':
                self.save_game()
                break


    def save_game(self):
        #open a new empty shelve (possibly overwriting an old one) to write the game data
        file = shelve.open('savegame', 'n')
        file['map'] = self.map.map
        file['objects'] =self.map.objects
        file['player_index'] = self.map.objects.index(self.player)
        file['inventory'] = self.inventory
        file['game_msgs'] = self.screen.game_msgs
        file['game_state'] = self.game_state
        file['dungeon_level'] = self.map.dungeon_level
        file['stairs_index'] = self.map.objects.index(self.map.stairs)
        file.close()


    def load_game(self):
        #open the previously saved shelve and load the game data
        file = shelve.open('savegame', 'r')
        self.map.map = file['map']
        self.map.objects = file['objects']
        self.player =self.map.objects[file['player_index']]
        self.map.player = player
        self.inventory = file['inventory']
        self.screen.game_msgs = file['game_msgs']
        self.game_state = file['game_state']
        self.map.dungeon_level = file['dungeon_level']
        self.map.stairs = self.map.objects[file['stairs_index']]
        file.close()

        self.initialize_fov()

    def main_menu(self):
        img = libtcod.image_load('menu_background.png')        
        while not libtcod.console_is_window_closed():
            #show the background image, at twice the regular console resolution
            libtcod.image_blit_2x(img, 0, 0, 0)

            #show the game's title and some credits!
            libtcod.console_set_default_foreground(0, libtcod.light_yellow)
            libtcod.console_print_ex(0, Screen.SCREEN_WIDTH / 2, Screen.SCREEN_HEIGHT / 2 - 4, libtcod.BKGND_NONE, libtcod.CENTER,
                                     'TOMBS OF THE ANCIENT KINGS')
            libtcod.console_print_ex(0, Screen.SCREEN_WIDTH / 2, Screen.SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER,
                                     'By Steven')

            #show options and wait for the player's choice
            choice = self.screen.menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

            if choice == 0: #new game
                self.new_game()
                self.play_game()
            elif choice == 1:
                try:
                    self.load_game()
                except:
                    self.screen.msgbox('\n No saved game to load!\n', 24)
                    continue
                self.play_game()
            elif choice == 2: #quit
                break