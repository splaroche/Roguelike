#################################################################################
# The map module contains classes that deal with objects the make up the map
# or that appear on the map.
# Note: The Object class should be here, but it's in its own module to prevent
#       circular import issues.
#################################################################################
import creatures, items, gui, character_classes, objects
import libtcodpy as libtcod
__author__ = 'Steven'

#################################################################################
# The GameMap represents the dungeon map, and the objects associated with it.
#################################################################################
class GameMap:
    # FOV Constants
    FOV_ALGO = 0 #default
    FOV_LIGHT_WALLS = True
    TORCH_RADIUS = 10

    # Room size Constants
    ROOM_MAX_SIZE = 10
    ROOM_MIN_SIZE = 6
    MAX_ROOMS = 30
    
    #The original player position on the first level of the map.
    #Used when the player respawns.
    orig_player_x = 0
    orig_player_y = 0
    
    def __init__(self):
        self.map = None
        self.objects = []
        self.stairs = None
        self.dungeon_level = 1
        self.player = None
        self.screen = None
        
    ####################################################################################################
    # Room Creation
    ####################################################################################################
    #Create a horizontal tunnel from point x1 to x2 on y.
    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].block_sight = False

    #Create a vertical tunnel from point y1 to y2 on x.
    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].block_sight = False

    #Creates a room from a rectangle object.
    def create_room(self, room):
        #go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.map[x][y].blocked = False
                self.map[x][y].block_sight = False

    ####################################################################################################
    # Map Methods
    ####################################################################################################
    #Checks if the point is blocked, either because the map point is blocked, or there's a blockable 
    #object in the point.
    def is_blocked(self, x, y):
        #first test the map tile
        if self.map[x][y].blocked:
            return True

        #now check for any blocking objects
        for object in self.objects:
            if object.blocks and object.x == x and object.y == y:
                return True

        return False
    
    #Make the map.
    def make(self):
        
        #fill map with unblocked tiles
        self.map = [[Tile(True)
                for y in range(gui.Screen.MAP_HEIGHT)]
               for x in range(gui.Screen.MAP_WIDTH)]

        #create rooms
        rooms = []
        num_rooms = 0
        for r in range(self.MAX_ROOMS):
            #random width and height
            w = libtcod.random_get_int(0, self.ROOM_MIN_SIZE, self.ROOM_MAX_SIZE)
            h = libtcod.random_get_int(0, self.ROOM_MIN_SIZE, self.ROOM_MAX_SIZE)
            #random position without going out of the boundaries of the map
            x = libtcod.random_get_int(0, 0, gui.Screen.MAP_WIDTH - w - 1)
            y = libtcod.random_get_int(0, 0, gui.Screen.MAP_HEIGHT - h - 1)

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
                
                #if this is the first room, place the player.
                if num_rooms == 0:
                    self.player.x = new_x
                    self.player.y = new_y
                    
                    #if dungeon level is 1, set the starting position so that the player can 
                    #respawn when they die.
                    if self.dungeon_level == 1:
                        self.orig_player_x = new_x
                        self.orig_player_y = new_y
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
        self.stairs = objects.Object(new_x, new_y, '<', 'stairs', libtcod.white, always_visible=True)
        self.objects.append(self.stairs)
        self.stairs.send_to_back(self.objects)

    #Place the objects on the map, including monsters and items
    #NOTE: 09/02/13 - This method is being changed for better placement.
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
                    fighter_component = character_classes.BaseCharacterClass(hp=20, defense=0, power=4)
                    ai_component = creatures.BasicMonster()
                    monster = creatures.Creature(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True,
                        character_class=fighter_component, ai=ai_component, xp=35, screen=self.screen)
                elif choice == 'troll':
                    #create a troll
                    fighter_component = character_classes.BaseCharacterClass(hp=30, defense=2, power=8)
                    ai_component = creatures.BasicMonster()
                    monster = creatures.Creature(x, y, 'T', 'troll', libtcod.darker_green, blocks=True,
                                     character_class=fighter_component, ai=ai_component, xp=100, screen=self.screen)
                monster.character_class.player = self.player
                self.objects.append(monster)

        #maximum number of items per room
        max_items = self.from_dungeon_level([[1, 1], [2, 4]])

        #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
        item_chances = {}
        item_chances['heal'] = 35 #healing potion always shows up, even if all other items have 0 chance
        item_chances['lightning'] = self.from_dungeon_level([[25, 4]])
        item_chances['fireball'] = self.from_dungeon_level([[25, 6]])
        item_chances['confuse'] = self.from_dungeon_level([[10, 2]])
        item_chances['sword'] = self.from_dungeon_level([[10, 3]])

        num_items = libtcod.random_get_int(0, 0, max_items)

        for i in range(num_items):
            #choose random spot for this item
            x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
            y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

            #only place it if the tiles is not blocked
            if not self.is_blocked(x, y):
                choice = self.random_choice(item_chances)
                item = items.Item(x, y, '?','', libtcod.white)
                if choice == 'heal':
                    #create a healing potion
                    item = items.Spell_Scroll(x, y, '!', 'healing potion', libtcod.violet, 'heal')
                elif choice == 'lightning':
                    #create a lightning bolt scroll
                    item = items.Spell_Scroll(x, y, '#', 'scroll of lightning bolt', libtcod.dark_blue, 'lightning')
                elif choice == 'fireball':
                    #create a fireball scroll
                    item = items.Spell_Scroll(x, y, '#', 'scroll of fireball', libtcod.dark_orange, 'fireball')
                elif choice == 'confuse':
                    #create a confuse scroll
                    item = items.Spell_Scroll(x, y, '#', 'scroll of confusion', libtcod.light_blue, 'confusion')
                elif choice == 'sword':                    #create a sword                    
                    item = items.Equipment(x, y, '/', 'sword', libtcod.sky, slot='right hand')
                self.objects.append(item)
                item.send_to_back(self.objects) # items appear below other objects

    #Make the next map level and proceed to it.
    def next_level(self):
        #advance to the next level
        self.screen.message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
        self.player.heal_self(self.player.character_class.max_hp / 2)

        self.screen.message('After a rare moment of peace, you descend deeper into the hear of the dungeon...', libtcod.red)
        self.dungeon_level += 1
        self.make() #create a fresh level!

        self.initialize_fov()
    #Returns a value that depends on level.  The table specifies what value occurs after each level, default is 0
    def from_dungeon_level(self, table):
        
        for (value, level) in reversed(table):
            if self.dungeon_level >= level:
                return value
        return 0
    
    #Creates a random index based on the list of chances.
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

    #Generates a random choice based on the passed in dictionary.
    def random_choice(self, chances_dict):
        #choose one option from dictionary of chances, returning its key
        chances = chances_dict.values()
        strings = chances_dict.keys()

        return strings[self.random_choice_index(chances)]
    
    #Create the FOV and paint the screen with it.
    def initialize_fov(self):        

        libtcod.console_clear(self.screen.con) #unexplored areas start black
        self.screen.fov_recompute = True

        #create the FOV map, according to the generated map
        self.screen.fov_map = libtcod.map_new(self.screen.MAP_WIDTH, self.screen.MAP_HEIGHT)
        for y in range(self.screen.MAP_HEIGHT):
            for x in range(self.screen.MAP_WIDTH):
                libtcod.map_set_properties(self.screen.fov_map, x, y, not self.map[x][y].block_sight, not self.map[x][y].blocked)

    #Targets a monster. Returns a clicked monster inside FOV up to a range, or None if right-clicked  
    def target_monster(self, max_range=None):        
        while True:
            (x, y) = self.screen.target_tile(map=self, max_range=max_range)
            if x is None: #player cancelled
                return None
            
            for obj in self.objects:
                #if the object is a creature, return it.
                if obj.x == x and obj.y == y and isinstance(obj, creatures.Creature) and obj != self.player:
                    return obj
                
    #Returns the closest monster to the player. 
    def closest_monster(self, max_range):
        #find closest enemy, up to a maximum range, and in the player's FOV
        closest_enemy = None
        closest_dist = max_range + 1 #start with (slightly more than) maximum range

        for object in self.objects:
            #check that the object is a monster and visible.
            if isinstance(object,creatures.Creature) and not object == self.owner and libtcod.map_is_in_fov(self.screen.fov_map, object.x, object.y):
                #calculate distance between this object and the player
                dist = self.player.distance_to(object)
                if dist < closest_dist: #it's closer, so remember it
                    closest_enemy = object
                    closest_dist = dist
        return closest_enemy

    #Updates the monster bindings to point to the player.  Called when the player respawns
    def update_player_bindings(self):
        for obj in self.objects:
            if isinstance(obj, creatures.Creature) and obj != self.player and obj.character_class is not None: 
                obj.player = self.player

#################################################################################
# Rectangle class is used for room creation.
#################################################################################
class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
    
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return center_x, center_y

    def intersect(self, other):
        #returns true if this rectangle interests with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y2)

#################################################################################
# A Tile represents a point on the map.
#################################################################################
class Tile:
    # a tile of the map
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        #by default, if a tiles is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight

        self.explored = False


