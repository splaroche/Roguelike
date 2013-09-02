import libtcodpy as libtcod
from gui import Screen
from objects import Object
import items
# A creature class. A creature is defined as anything that is alive, like Monsters or the Player.

# the creature inherits from Object
class Creature(Object):
    
    
    def __init__(self, x, y, char, name, color, blocks=True, ai=None, item=None, always_visible=False,
                 equipment=None, character_class=None, creature_type=None, xp=0, screen=None):
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

        self.inventory = []

        self.screen = screen
        if self.screen:
            self.character_class.screen = screen
        
        self.dead = False
        
        self.level = 1
        self.equipment = {'head': None, 'body':None, 'legs':None, 'hands':None, 'feet':None, 'left hand': None, 'right hand': None}
        
    def drop_item(self, item, screen):
        # special case if it's an equipped item
        if isinstance(item, items.Equipment) and item.is_equipped:
            self.equipment.remove(item)
            item.dequip(screen)
        else :
            #remove from the player's inventory.  also, place it at the player's coordinates                        
            self.inventory.remove(item)
        item.x = self.x
        item.y = self.y

        
        screen.message('You dropped a ' + item.name + '.', libtcod.yellow)

    #an item that can be picked up and used
    def pick_up_item(self, item, screen):
        item.owner = self
        #add to the player's inventory and remove from the map
        if len(self.inventory) >= 25:
            screen.message('Your inventory is full, cannot pick up ' + item.name + '.', libtcod.red)
        else:
            self.inventory.append(item)
            screen.message('You picked up a ' + item.name + '!', 'green')

            #special case: automatically equip, if the corresponding equipment slot is unused
            if isinstance(item, items.Equipment):
                equipment = self.equipment
                if equipment and self.get_equipped_in_slot(item.slot) is None:
                    equipment.equip()

    def get_equipped_in_slot(self, slot): # returns the equipment in a slot, or None if it's empty
        for obj in self.equipment:
            if obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj.equipment
        return None

    def get_all_equipped(self):  #returns a list of equipped items
        return [v for k, v in self.equipment.iteritems() if v is not None]
    
    
    


    ####################################################################################################
    # Death Methods
    ####################################################################################################
    def death(self, objects):
        #transform it into a nasty corpse! it doesn't block, can't be attacked and doesn't move
        self.screen.message(self.name.capitalize() + ' is dead! You gain ' + str(self.xp) + ' experience points!',
                libtcod.orange)
        self.char = '%'
        self.color = libtcod.dark_red
        self.blocks = False
        self.character_class = None
        self.ai = None
        self.name = 'Remains of ' + self.name
        self.dead = True
        self.send_to_back(objects)



#########################################################################
# AI classes
#########################################################################
class BasicMonster:
       
    #AI for a basic monster
    def take_turn(self, player, map) :
        #a basic monster takes its turn.  If you can see it, it can see you
        monster = self.owner        
        if libtcod.map_is_in_fov(monster.screen.fov_map, monster.x, monster.y):
            #move towards player if far away
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y, map)

            #close enough, attack! (if the player is still alive.)
            elif player.character_class.hp > 0:
                monster.character_class.attack(player, map.objects)


class ConfusedMonster:
    #AI for a temporarily confused monster (reverts to previous AI after a while)
    def __init__(self, old_ai, num_turns=0):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self, player, map):
        if self.num_turns > 0: #still confused
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1), map)
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
    def __init__(self, x, y, char, name, color, character_class, blocks=True, equipment=[], screen=None):
           Creature.__init__(self, x=x, y=y, char=char, name=name, color=color, blocks=True, ai=None, always_visible=True, 
                equipment=equipment, character_class=character_class, screen=screen)
     
    # Moves the player into a square.  If the square contains a living monster, attack    
    def move_or_attack(self, dx, dy, objects, map):

        #the coordinates the player is moving to/attacking
        x = self.x + dx
        y = self.y + dy

        #try to find an attackable object there
        target = None
        for object in objects:
            if isinstance(object,Creature) and object != self and object.x == x and object.y == y:
                if not object.dead:
                    target = object
                    break

        #attack if target found, move otherwise
        if target is not None:
            self.character_class.attack(target, objects)
            return False
        else:
            self.move(dx, dy, map)
            return True

    def character_screen(self):
        
        # determine the player's xp progression
        level_up_xp = self.character_class.LEVEL_UP_BASE + self.level * self.character_class.LEVEL_UP_FACTOR
                    
        char_screen = 'Character Information\n\nLevel: ' + str(self.level) + '\nExperience: ' + str(
                        self.xp) + '\nExperience to level up: ' + str(
                        level_up_xp) + '\n\nMaximum HP: ' + str(
                        self.character_class.max_hp) + '\nAttack: ' + str(
                        self.character_class.power) + '\nDefense: ' + str(
                        self.character_class.defense) + '\n\nEquipped Items: '
                        
        l = self.get_all_equipped()
        for item in l:
            char_screen += '\n' + item.slot.capitalize() + ': ' + item.name.capitalize()
             
        return char_screen
                        
    # Run when the player dies
    def death(self, objects):
        #the game ended!
        self.screen.message('You died!', libtcod.red)        

        #for added effect, transform the player into a corpse!
        self.char = '%'
        self.color = libtcod.dark_red
        self.name = 'Dead body'
        self.blocks = False
        self.always_visible = False
        
        #set the dead flag
        self.dead = True
        
        #draw it below other objects
        self.send_to_back(objects)