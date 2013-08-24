from map import Map
from screen import Screen
from object import Object
import libtcodpy as libtcod
class Game:
    def __init__(self):
        self.player = None
        self.player_action = None
        self.inventory = []
        self.game_msgs = []
        self.game_state = None
        self.dungeon_level = None
        self.map = Map()
        self.screen = Screen()
    ####################################################################################################
    # Game Initialization Methods
    ####################################################################################################
    def new_game(self):

        #create object representing the player
        fighter_component = Base_Character(hp=100, defense=1, power=4, xp=0, death_function=player_death)
        player = Player(Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component), fighter_component)
        o = Player.get_instance()
        print o.name
        player.level = 1

        #set the dungeon level
        dungeon_level = 1

        #generate map (at this point it's not drawn to the screen
        self.map.make_map()

        #generate the FOV
        self.initialize_fov()

        self.game_state = 'playing'
        self.inventory = []

        #create the list of game messages and their colors, starts empty
        self.game_msgs = []

        #a warm welcoming message!
        screen.message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', 'red')


    def initialize_fov(self):        

        libtcod.console_clear(con) #unexplored areas start black
        screen.fov_recompute = True

        #create the FOV map, according to the generated map
        screen.fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                libtcod.map_set_properties(screen.fov_map, x, y, not self.map[x][y].block_sight, not self.map[x][y].blocked)


    def play_game(self):

        self.player_action = None

        self.screen.mouse = libtcod.Mouse()
        self.screen.key = libtcod.Key()
        while not libtcod.console_is_window_closed():
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, self.screen.key, self.screen.mouse)
            self.screen.render_all()

            libtcod.console_flush()

            #check for levelups
            Player.get_instance().check_level_up()

            #handle keys and exit game if needed
            for object in self.map.objects:
                object.clear()
            self.player_action = screen.handle_keys()

            #let monsters take their turn
            if self.game_state == 'playing' and self.player_action != 'didnt-take-turn':
                for object in self.map.objects:
                    if object.ai:
                        object.ai.take_turn()

            if self.player_action == 'exit':
                self.save_game()
                break


    def save_game(self):
        #open a new empty shelve (possibly overwriting an old one) to write the game data
        file = shelve.open('savegame', 'n')
        file['map'] = self.map.map
        file['objects'] = self.map.objects
        file['player_index'] = self.map.objects.index(Player.get_instance())
        file['inventory'] = self.inventory
        file['game_msgs'] = self.game_msgs
        file['game_state'] = self.game_state
        file['dungeon_level'] = self.dungeon_level
        file['stairs_index'] = self.map.objects.index(self.map.stairs)
        file.close()


    def load_game(self):
        #open the previously saved shelve and load the game data
        global map, objects, player, inventory, game_msgs, game_state, dungeon_level, stairs

        file = shelve.open('savegame', 'r')
        self.map.map = file['map']
        self.map.objects = file['objects']
        Player.get_instance(player=objects[file['player_index']])
        self.inventory = file['inventory']
        self.game_msgs = file['game_msgs']
        self.game_state = file['game_state']
        self.dungeon_level = file['dungeon_level']
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
                    screen.msgbox('\n No saved game to load!\n', 24)
                    continue
                self.play_game()
            elif choice == 2: #quit
                break