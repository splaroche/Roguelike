
import shelve
from baseCharacter import Base_Character
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
# Death Methods
####################################################################################################
def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be attacked and doesn't move
    message(monster.name.capitalize() + ' is dead! You gain ' + str(monster.fighter.xp) + ' experience points!',
            libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()


def player_death(player):
    #the game ended!
    global game_state
    message('You died!', libtcod.red)
    game_state = 'dead'

    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red


####################################################################################################
# Movement Methods
####################################################################################################

class Game:
    def __init__(self):
        self.player = None
        self.inventory = []
        self.game_msgs = []
        self.game_state = None
        self.dungeon_level = None
        self.map = Map()

    ####################################################################################################
    # Game Initialization Methods
    ####################################################################################################
    def new_game(self):

        #create object representing the player
        fighter_component = Base_Character(hp=100, defense=1, power=4, xp=0, death_function=player_death)
        player = Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component)

        player.level = 1

        #set the dungeon level
        dungeon_level = 1

        #generate map (at this point it's not drawn to the screen
        map.make_map()

        #generate the FOV
        self.initialize_fov()

        game_state = 'playing'
        inventory = []

        #create the list of game messages and their colors, starts empty
        game_msgs = []

        #a warm welcoming message!
        Screen.message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', 'red')


    def initialize_fov(self):
        global fov_recompute, fov_map

        libtcod.console_clear(con) #unexplored areas start black
        fov_recompute = True

        #create the FOV map, according to the generated map
        fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)


    def play_game(self):
        global key, mouse, player_action

        player_action = None

        mouse = libtcod.Mouse()
        key = libtcod.Key()
        while not libtcod.console_is_window_closed():
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
            render_all()

            libtcod.console_flush()

            #check for levelups
            check_level_up()

            #handle keys and exit game if needed
            for object in objects:
                object.clear()
            player_action = handle_keys()

            #let monsters take their turn
            if game_state == 'playing' and player_action != 'didnt-take-turn':
                for object in objects:
                    if object.ai:
                        object.ai.take_turn()

            if player_action == 'exit':
                save_game()
                break


    def save_game(self):
        #open a new empty shelve (possibly overwriting an old one) to write the game data
        file = shelve.open('savegame', 'n')
        file['map'] = self.map.map
        file['objects'] = self.objects
        file['player_index'] = objects.index(player)
        file['inventory'] = inventory
        file['game_msgs'] = game_msgs
        file['game_state'] = game_state
        file['dungeon_level'] = self.dungeon_level
        file['stairs_index'] = objects.index(stairs)
        file.close()


    def load_game(self):
        #open the previously saved shelve and load the game data
        global map, objects, player, inventory, game_msgs, game_state, dungeon_level, stairs

        file = shelve.open('savegame', 'r')
        map = file['map']
        objects = file['objects']
        player = objects[file['player_index']]
        inventory = file['inventory']
        game_msgs = file['game_msgs']
        game_state = file['game_state']
        dungeon_level = file['dungeon_level']
        stairs = objects[file['stairs_index']]
        file.close()

        initialize_fov()






Menu.main_menu()