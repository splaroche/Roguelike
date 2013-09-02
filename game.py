from map import GameMap
from objects import Object
from character_classes import BaseCharacterClass
from creatures import Player, Creature
from gui import Screen
import libtcodpy as libtcod
import shelve, pickle, items
class Game:
    def __init__(self):
        self.player = None
        self.player_action = None
        self.inventory = []
        self.game_state = None      
        self.map = GameMap()
        self.screen = Screen()
        self.map.screen = self.screen
    
    def initialize_new_player(self):
        fighter_component = BaseCharacterClass(hp=100, defense=1, power=4)
        self.player = Player(self.map.orig_player_x, self.map.orig_player_y, '@', 'player', libtcod.white, blocks=True, character_class=fighter_component, screen=self.screen)
        self.player.equipment['right hand'] = items.Equipment(0, 0, '/', 'sword', libtcod.light_blue, 'right hand', power_bonus=2)
        
        self.map.player = self.player
        self.map.objects.append(self.player)
    
    ####################################################################################################
    # Game Initialization Methods
    ####################################################################################################
    def new_game(self):

        #create object representing the player
        self.initialize_new_player()       

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
            self.player.character_class.check_level_up()

            #handle keys and exit game if needed
            for object in self.map.objects:
                object.clear(self.screen.con)
            self.player_action = self.screen.handle_keys(self.game_state, self.player, self.map.objects, self.map)
            #exit the game if the player select so
            if self.player_action == 'exit':
                self.save_game()
                break
            #let monsters take their turn
            if self.game_state == 'playing' and self.player_action != 'didnt-take-turn':
                for object in self.map.objects:
                    if isinstance(object, Creature) and object.name != 'player' and not object.dead:
                        #take monster turns and check to see if monsters have killed the player.
                        object.ai.take_turn(self.player, self.map)
                        
                        #if monsters have killed the player, spawn a new player
                        #set it at the original start of the dungeon
                        if self.player.dead:
                            
                            #assign the player object and add it to the objects tree.                            
                            self.initialize_new_player()
                            #update the creatures player bindings
                            self.map.update_player_bindings()

        

    def save_game(self):
        #open a new empty shelve (possibly overwriting an old one) to write the game data
#         file = open('savegame.sav', 'wb')
#         pickle.dump(self.map, file)
#         pickle.dump(self.map.objects, file)
#         pickle.dump(self.player, file)
#         pickle.dump(self.screen, file)
#         pickle.dump(self.screen.game_msgs, file)
#         pickle.dump(self.screen.fov_recompute, file)
#         pickle.dump(self.screen.fov_map, file)
#         pickle.dump(self.game_state, file)
#         pickle.dump(self.map.stairs, file)
        file = shelve.open('savegame.s', 'n')
        file['map'] = self.map
        file['objects'] = self.map.objects
        file['player'] = self.player
        file['game_msgs'] = self.screen.game_msgs
        file['fov_map'] = self.screen.fov_map
        file['fov_recompute'] = self.screen.fov_recompute
        file['game_state'] = self.game_state
        file['stairs'] = self.map.stairs
        file.close()


    def load_game(self):
        #open the previously saved shelve and load the game data
#        file = open('savegame.sav', 'rb')
#         self.map = pickle.load(file)
#         self.map.objects = pickle.load(file)
#         self.player = pickle.load(file)
#         self.map.player = self.player        
#         self.screen = Screen()
#         self.screen.game_msgs = pickle.load(file)
#         self.screen.fov_map = pickle.load(file)
#         self.screen.fov_recompute = pickle.load(file)
#         self.game_state = pickle.load(file)
#         self.map.stairs = pickle.load(file)
        file = shelve.open('savegame.s', 'r')
        self.map = file['map']
        self.map.objects = file['objects']
        self.player = file['player']
        self.screen.fov_map = file['fov_map']
        self.screen.fov_recompute = file['fov_recompute']
        self.screen.game_msgs = file['game_msgs']
        self.game_state = file['game_state']
        self.map.stairs = file['stairs']
               
        file.close()
        self.map.player = self.player
        self.map.screen = self.screen
        self.map.update_player_bindings()
        self.map.initialize_fov()
        libtcod.sys_set_fps(self.screen.LIMIT_FPS)
                
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