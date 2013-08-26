import libtcodpy as libtcod
from gui import Screen
from objects import Object
# A creature class. A creature is defined as anything that is alive, like Monsters or the Player.

# the creature inherits from Object
class Creature(Object):

    def __init__(self, x, y, char, name, color, blocks=True, ai=None, item=None, always_visible=False,
                 equipment=None, character_class=None, creature_type=None, xp=0):
        Object.__init__(self, x, y, char, name, color, blocks=blocks, always_visible=always_visible)
        self.xp = xp
        self.character_class = character_class
        if self.character_class:
            # let the fighter component know who owns it
            self.character_class.owner = self

        self.ai = ai
        if self.ai:
            # let the ai component know who owns it
            self.ai.owner = self

        self.item = item
        if self.item:
            self.item.owner = self

        self.equipment = equipment
        
    ####################################################################################################
    # Death Methods
    ####################################################################################################
    def death(self):
        #transform it into a nasty corpse! it doesn't block, can't be attacked and doesn't move
        Screen.get_instance().message(self.name.capitalize() + ' is dead! You gain ' + str(self.xp) + ' experience points!',
                libtcod.orange)
        self.char = '%'
        self.color = libtcod.dark_red
        self.blocks = False
        self.character_class = None
        self.ai = None
        self.name = 'Remains of ' + self.name
        self.send_to_back()



#########################################################################
# AI classes
#########################################################################
class BasicMonster:
    def __init__(self, player, fov_map):
        self.fov_map = fov_map
        self.player = player

    #AI for a basic monster
    def take_turn(self):
        #a basic monster takes its turn.  If you can see it, it can see you
        monster = self.owner
        if libtcod.map_is_in_fov(self.fov_map, monster.x, monster.y):

            #move towards player if far away
            if monster.distance_to(self.player) >= 2:
                monster.move_towards(self.player.x, self.player.y)

            #close enough, attack! (if the player is still alive.)
            elif self.player.character_class.hp > 0:
                monster.character_class.attack(self.player)


class ConfusedMonster:
    #AI for a temporarily confused monster (reverts to previous AI after a while)
    def __init__(self, old_ai, num_turns=0):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0: #still confused
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else: #restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            return ('The ' + self.owner.name + ' is no longer confused!', libtcod.red)

#################################################################################
# The player class stores all the player details.  It inherits from the creature
# class, but contains specific player related methods. 
# The class is accesbile as a singleton by calling get_instance()
#################################################################################
class Player(Creature):    
    def __init__(self, x, y, char, name, color, character_class, blocks=True, equipment=[]):
           Creature.__init__(self, x=x, y=y, char=char, name=name, color=color, blocks=True, ai=None, always_visible=True, 
                equipment=equipment, character_class=character_class)
     
    # Moves the player into a square.  If the square contains a living monster, attack    
    def move_or_attack(self, dx, dy, objects, map):

        #the coordinates the player is moving to/attacking
        x = self.x + dx
        y = self.y + dy

        #try to find an attackable object there
        target = None
        for object in objects:
            if object is Creature and object.name != player and object.x == x and object.y == y:
                target = object
                break

        #attack if target found, move otherwise
        if target is not None:
            self.character_class.attack(target)
            return False
        else:
            self.move(dx, dy, map)
            return True

    # Run when the player dies
    def death(self):
        #the game ended!
        Screen.get_instance().message('You died!', libtcod.red)        

        #for added effect, transform the player into a corpse!
        self.char = '%'
        self.color = libtcod.dark_red

        #return a game state string
        return 'dead'