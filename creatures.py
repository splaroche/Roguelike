#################################################################################
# The creatures module contains classes that are living things (like the player)
# and classes directly dealing with them like monster ai.
#################################################################################

import libtcodpy as libtcod
from objects import Object
import items

#################################################################################
# The Creature is defined as anything that is alive, like Monsters or the Player.
# The Creature inherits from Object.
#################################################################################
class Creature(Object):
    def __init__(self, x, y, char, name, color, blocks=True, ai=None, always_visible=False,
                 equipment=None, character_class=None, creature_type=None, xp=0, screen=None):
        #call super constructor to create the map object
        Object.__init__(self, x, y, char, name, color, blocks=blocks, always_visible=always_visible)
        self.character_class = character_class
        if self.character_class:
            # let the fighter component know who owns it
            self.character_class.owner = self
        
        self.screen = screen
        if self.screen:
            # set the screen element in the character_class
            self.character_class.screen = screen        
        
        self.ai = ai
        if self.ai:
            # let the ai component know who owns it
            self.ai.owner = self        
        
        self.xp = xp            
        self.dead = False
        self.inventory = []        
        #set the default equipment dictionary.
        self.equipment = {'head': None, 'body':None, 'legs':None, 'hands':None, 'feet':None, 'left hand': None, 'right hand': None}
        self.player = None
        
    #Drops the item selected in the drop inventory item screen.
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

    #Picks up an item from the map.  If it's a piece of equipment, equip it.
    def pick_up_item(self, item, screen):
        #set the onwer the creature
        item.owner = self
        #add to the player's inventory and remove from the map
        if len(self.inventory) >= 25:
            screen.message('Your inventory is full, cannot pick up ' + item.name + '.', libtcod.red)
        else:
            self.inventory.append(item)
            screen.message('You picked up a ' + item.name + '!', 'green')

            #special case: automatically equip, if the corresponding equipment slot is unused
            if isinstance(item, items.Equipment):                                               
                if self.equipment and self.get_equipped_in_slot(item.slot) is None:                    
                    item.equip()

    #Returns the equipment in a slot, or None if it's empty
    def get_equipped_in_slot(self, slot): 
        return self.equipment[slot]

    #Gets all equipped equipment and returns a list.
    def get_all_equipped(self):  
        return [v for k, v in self.equipment.iteritems() if v is not None]
    
    #Converts the creature to a dead body, changing the char, and color, and prints a message.
    def death(self, objects):
        #transform it into a nasty corpse! it doesn't block, can't be attacked and doesn't move
        self.screen.message(self.name.capitalize() + ' is dead! You gain ' + str(self.xp) + ' experience points!',
                libtcod.orange)
        self.char = '%'
        self.color = libtcod.dark_red
        self.blocks = False
        
        #clear the character_class and ai to prevent the dead body from moving around!
        self.character_class = None
        self.ai = None
        self.name = 'Remains of ' + self.name        
        self.dead = True
        
        #send it to the back so things get painted over.
        self.send_to_back(objects)
    
    #Heal the Creature by X amount.
    def heal_self(self, amount):
        #heal by the given amount, without going over the maximum
        self.character_class.hp += amount
        if self.character_class.hp > self.character_class.max_hp:
            self.character_class.hp = self.character_class.max_hp

    #Take damage in X amount.
    def take_damage(self, damage, objects):
        #apply damage if possible
        if damage > 0:
            self.character_class.hp -= damage

        #check for death.  call the death function    
        if self.character_class.hp <= 0:
            self.death(objects)

            #yield experience to the player
            if self.player:
                self.player.xp += self.xp
    
    #Checks and levels up the Creature
    def check_level_up(self):
        #see if the player's experience is enough to level-up
        level_up_xp = self.character_class.LEVEL_UP_BASE + self.character_class.level + self.character_class.LEVEL_UP_FACTOR
        if self.xp >= level_up_xp:
            #it is! level up
            self.character_class.level += 1
            self.xp -= level_up_xp
            self.screen.menu('Your battle skills grow stronger! You reached level ' + str(self.character_class.level) + '!', 'yellow')

            choice = None
            while choice is None: #keep asking until a choice is made
                choice = self.screen.menu('Level up! Choose a stat to raise:\n',
                                   ['Constitution (+20 HP, from ' + str(self.character_class.max_hp) + ')',
                                    'Strength (+1 attack, from ' + str(self.character_class.power) + ')',
                                    'Agility (+1 defense, from ' + str(self.character_class.defense) + ')'],
                                   self.character_class.LEVEL_SCREEN_WIDTH)

            if choice == 0: #hp
                self.character_class.base_max_hp += 20
                self.character_class.hp += 20
            elif choice == 1: #power
                self.character_class.base_power += 1
            elif choice == 2: #defense
                self.character_class.base_defense += 1
                
                
#################################################################################
# The player class stores all the player details.  It inherits from the Creature
# class, but contains specific player related methods. 
#################################################################################
class Player(Creature):            
    def __init__(self, x, y, char, name, color, character_class, blocks=True, equipment=[], screen=None):
        # call the super constructor
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

    #Returns a string with the character screen information, including level, experience, stats and items.
    def character_screen(self):
        
        # determine the player's xp progression
        level_up_xp = self.character_class.LEVEL_UP_BASE + self.character_class.level * self.character_class.LEVEL_UP_FACTOR
                    
        char_screen = 'Character Information\n\nLevel: ' + str(self.character_class.level) + '\nExperience: ' + str(
                        self.xp) + '\nExperience to level up: ' + str(
                        level_up_xp) + '\n\nMaximum HP: ' + str(
                        self.character_class.max_hp) + '\nAttack: ' + str(
                        self.character_class.power) + '\nDefense: ' + str(
                        self.character_class.defense) + '\n\nEquipped Items: '
                        
        l = self.get_all_equipped()
        for item in l:
            char_screen += '\n' + item.slot.capitalize() + ': ' + item.name.capitalize()
             
        return char_screen
                        
    #Converts the player to a dead body, changing the char, and color, and prints a message.
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
        


#################################################################################
# AI classes
#################################################################################
#################################################################################
# The BasicMonster ai is used by default.  The monster will attack the player
# if the player is within sight.
#################################################################################
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

#################################################################################
# The ConfusedMonster ai is used when the player casts confusion on a monster.
#################################################################################
class ConfusedMonster:
    
    def __init__(self, old_ai, num_turns=0):
        #AI for a temporarily confused monster (reverts to previous AI after a while)
        self.old_ai = old_ai
        self.num_turns = num_turns

    #Confused monsters randomly walk until the num_turns is 0, then it returns to the old ai.
    def take_turn(self, player, map):
        if self.num_turns > 0: #still confused
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1), map)
            self.num_turns -= 1
        else: #restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            return ('The ' + self.owner.name + ' is no longer confused!', libtcod.red)
