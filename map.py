from ai import *
from equipment import Equipment
from baseCharacter import Base_Character
from menu import Menu
from object import Object
from screen import Screen
import libtcodpy as libtcod
from item import Item
from rectangle import Rect
from tile import Tile
__author__ = 'Steven'


class Map:

    # FOV Constants
    FOV_ALGO = 0 #default
    FOV_LIGHT_WALLS = True
    TORCH_RADIUS = 10

    # Room size Constants
    ROOM_MAX_SIZE = 10
    ROOM_MIN_SIZE = 6
    MAX_ROOMS = 30

    def __init__(self, player):
        self.map = None
        self.objects = []
        self.player = player
        self.stairs = None
    ####################################################################################################
    # Room Creation
    ####################################################################################################
    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].block_sight = False

    def create_room(self, room):
        #go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.map[x][y].blocked = False
                self.map[x][y].block_sight = False

    ####################################################################################################
    # Map Methods
    ####################################################################################################
    def is_blocked(self, x, y):
        #first test the map tile
        if self.map[x][y].blocked:
            return True

        #now check for any blocking objects
        for object in self.objects:
            if object.blocks and object.x == x and object.y == y:
                return True

        return False

    def make_map(self):

        #the list of objects with just the player
        self.objects = [self.player]

        #fill map with unblocked tiles
        self.map = [[Tile(True)
                for y in range(Screen.MAP_HEIGHT)]
               for x in range(Screen.MAP_WIDTH)]

        #create rooms
        rooms = []
        num_rooms = 0
        for r in range(self.MAX_ROOMS):
            #random width and height
            w = libtcod.random_get_int(0, self.ROOM_MIN_SIZE, self.ROOM_MAX_SIZE)
            h = libtcod.random_get_int(0, self.ROOM_MIN_SIZE, self.ROOM_MAX_SIZE)
            #random position without going out of the boundaries of the map
            x = libtcod.random_get_int(0, 0, self.MAP_WIDTH - w - 1)
            y = libtcod.random_get_int(0, 0, self.MAP_HEIGHT - h - 1)

            new_room = Rect(x, y, w, h)

            #run through the other rooms and see if they intersect with this one
            failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

            if not failed:
                #this means there are no intersections, so this room is valid

                #"paint" it to the map's tiles
                self.create_room(new_room)

                #center coordinates of new room, will be useful
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    self.player.x = new_x
                    self.player.y = new_y
                else:
                    #all rooms after the first:
                    #connect it to the previous room with a tunnel

                    #center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    #draw a coin
                    if libtcod.random_get_int(0, 0, 1) == 1:
                        #first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        #first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                #add monsters
                self.place_objects(new_room)

                #finally append the new rooms to the list
                rooms.append(new_room)
                num_rooms += 1

        #create stairs at the center of the last room
        self.stairs = Object(new_x, new_y, '<', 'stairs', libtcod.white, always_visible=True)
        self.objects.append(self.stairs)
        self.stairs.send_to_back()


    def place_objects(self, room):
        # maximum number of monsters per room
        max_monsters = self.from_dungeon_level([[2, 1], [3, 4], [5, 6]])

        #chance of each monster
        monster_chances = {}
        monster_chances['orc'] = 80 #orc always shows up, even if all other monsters have 0 chance
        monster_chances['troll'] = self.from_dungeon_level([[15, 3], [30, 5], [60, 7]])

        #choose random number of monsters
        num_monsters = libtcod.random_get_int(0, 0, max_monsters)

        for i in range(num_monsters):
            #choose random spot for this monster
            x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
            y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
            if not self.is_blocked(x, y):
                choice = self.random_choice(monster_chances)
                if choice == 'orc':
                    #create an orc
                    fighter_component = Base_Character(hp=20, defense=0, power=4, xp=35, death_function=monster_death)
                    ai_component = BasicMonster()
                    monster = Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True,
                elif choice == 'troll':
                    #create a troll
                    fighter_component = Base_Character(hp=30, defense=2, power=8, xp=100, death_function=monster_death)
                    ai_component = BasicMonster()
                    monster = Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True,
                                     class_name=fighter_component, ai=ai_component)

                self.objects.append(monster)

        #maximum number of items per room
        max_items = self.from_dungeon_level([[1, 1], [2, 4]])

        #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
        item_chances = {}
        item_chances['heal'] = 35 #healing potion always shows up, even if all other items have 0 chance
        item_chances['lightning'] = self.from_dungeon_level([[25, 4]])
        item_chances['fireball'] = self.from_dungeon_level([[25, 6]])
        item_chances['confuse'] = self.from_dungeon_level([[10, 2]])
        item_chances['sword'] = 25

        num_items = libtcod.random_get_int(0, 0, max_items)

        for i in range(num_items):
            #choose random spot for this item
            x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
            y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

            #only place it if the tiles is not blocked
            if not self.is_blocked(x, y):
                choice = random_choice(item_chances)
                if choice == 'heal':
                    #create a healing potion
                    item_component = Item(use_function=cast_heal)
                    item = Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)
                elif choice == 'lightning':
                    #create a lightning bolt scroll
                    item_component = Item(use_function=cast_lightning)
                    item = Object(x, y, '#', 'scroll of lightning bolt', libtcod.dark_blue, item=item_component)
                elif choice == 'fireball':
                    #create a fireball scroll
                    item_component = Item(use_function=cast_fireball)
                    item = Object(x, y, '#', 'scroll of fireball', libtcod.dark_orange, item=item_component)
                elif choice == 'confuse':
                    #create a confuse scroll
                    item_component = Item(use_function=cast_confusion)
                    item = Object(x, y, '#', 'scroll of confusion', libtcod.light_blue, item=item_component)
                elif choice == 'sword':
                    #create a sword
                    equipment_component = Equipment(slot='right hand')
                    item = Object(x, y, '/', 'sword', libtcod.sky, equipment=equipment_component)
                self.objects.append(item)
                item.send_to_back() # items appear below other objects

    def next_level(self):
        global dungeon_level
        #advance to the next level
        Menu.message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
        self.player.fighter.heal_self(self.player.fighter.max_hp / 2)

        Menu.message('After a rare moment of peace, you descend deeper into the hear of the dungeon...', libtcod.red)
        dungeon_level += 1
        self.make_map() #create a fresh level!

        self.initialize_fov()

    def from_dungeon_level(self, table):
        #returns a value that depends on level.  the table specifies what value occurs after each level, default is 0
        for (value, level) in reversed(table):
            if dungeon_level >= level:
                return value
        return 0

    def random_choice_index(self, chances):
        #choose one option from list of chances, returning its index
        #the dice will land on some number between 1 and the sum of the chances
        dice = libtcod.random_get_int(0, 1, sum(chances))

        #go through all chances, keeping the sum so far
        running_sum = 0
        choice = 0
        for w in chances:
            running_sum += w

            #see if the dice landed in the part that corresponds to this choice
            if dice <= running_sum:
                return choice
            choice += 1


    def random_choice(self, chances_dict):
        #choose one option from dictionary of chances, returning its key
        chances = chances_dict.values()
        strings = chances_dict.keys()

        return strings[self.random_choice_index(chances)]
