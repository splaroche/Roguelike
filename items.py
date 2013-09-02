#################################################################################
# The items module contains item and item related classes.
# NOTE: At the moment Spells is within this module for convenience, it will 
#       likely be moved later. 
#################################################################################

import libtcodpy as libtcod
import gui, creatures
from objects import Object
__author__ = 'Steven'

#################################################################################
# The Equipment class models a piece of equipment (armor, sword, etc).
#################################################################################
class Equipment(Object):    
    def __init__(self, x, y, char, name, color, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        Object.__init__(self, x, y, char, name, color, blocks=False, always_visible=False)        
        self.slot = slot
        self.is_equipped = False
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus

    #Equip or dequip an item, depending on if it's currently equipped.
    def toggle_equip(self):
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    #equip an item.  if there's another item currently in that slot, replace it.
    def equip(self):
        #if the slot is already being used, dequip whatever is there first
        old_equipment = self.owner.get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()

        #equip object and show a message about it
        self.is_equipped = True
        #remove it from inventory and add it to equipment
        self.owner.inventory.remove(self)
        self.owner.equipment[self.slot] = self
        self.owner.screen.message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)

    #dequip an item
    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped: return
        self.is_equipped = False
        
        #remove from equipment and add to inventory
        self.owner.equipment[self.slot] = None
        self.owner.inventory.add(self)
        
        self.owner.screen.message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)


#################################################################################
# The Item class represents anything that might be picked up and used.
#################################################################################
class Item(Object):
    def __init__(self, x, y, char, name, color, use_function=None):
        Object.__init__(self, x, y, char, name, color, blocks=False, always_visible=False)
        self.use_function = use_function        
  
    #Use the item.
    def use(self, screen, map=None):
        #just call the use_function if it is defined
        if self.use_function is None:
            screen.message('The ' + self.name + ' cannot be used.')
        else:
            if self.use_function(screen, map) != 'cancelled':
                self.owner.inventory.remove(self) #destroy after use, unless it was cancelled for some reason

#################################################################################
# The Spell class represents all castable spells which are represented as 
# methods.
# NOTE: 09/02/13 This class will form the basis of the magic system.
#################################################################################
class Spell:

    #Spell Constants
    #Heal
    HEAL_AMOUNT = 40
    #Lightning
    LIGHTNING_RANGE = 5
    LIGHTNING_DAMAGE = 40
    #Confusion
    CONFUSE_NUM_TURNS = 10
    CONFUSE_NUM_TURNS = 10
    CONFUSE_RANGE = 8
    #Fireball
    FIREBALL_RADIUS = 3
    FIREBALL_DAMAGE = 25

    def __init__(self, objects):
        self.objects = objects

    #Casts a fireball.  The player is asked to select a tile and everything within the range is 
    #damaged, including the player.
    def cast_fireball(self, screen, map):
        #ask the player for a target tile to throw a fireball at
        screen.message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
        (x, y) = screen.target_tile(map)
        screen.message('The fireball explodes, burning everything within ' + str(self.FIREBALL_RADIUS) + ' tiles!', libtcod.orange)
        
        for obj in map.objects: #damage every fighter in range, including the player
            if isinstance(obj, creatures.Creature) and obj.distance(x, y) <= self.FIREBALL_RADIUS:
                screen.message('The ' + obj.name + ' gets burned for ' + str(self.FIREBALL_DAMAGE) + ' hit points!', libtcod.orange)                
                obj.take_damage(self.LIGHTNING_DAMAGE, map.objects)

    #Casts a heal spell.  Health Potions use this method for convenience. 
    def cast_heal(self, screen, map):
        #heal the player
        if self.owner.character_class.hp == self.owner.character_class.max_hp:
            screen.message('You are already at full health!', libtcod.red)
            return 'cancelled'

        screen.message('Your wounds start to feel better!', libtcod.light_violet)
        self.owner.heal_self(self.HEAL_AMOUNT)

    #Casts a lightning bolt at the closest monster.
    def cast_lightning(self, screen, map):
        #find closest enemy (inside a maximum range) and damage it
        monster = map.closest_monster(self.LIGHTNING_RANGE)
        if monster is None: #no enemy found within maximum range
            screen.message('No enemy is close enough to strike.', libtcod.red)
            return 'cancelled'
        #zap it!
        screen.message('A lightning bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
                + str(self.LIGHTNING_DAMAGE) + ' hit points!', libtcod.light_blue)
        monster.take_damage(self.LIGHTNING_DAMAGE, map.objects)

    #Casts confusion on a monster that is selected by mouse click.
    def cast_confusion(self, screen, map):
        #ask the player for a target to confuse
        screen.message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
        monster = map.target_monster(self.CONFUSE_RANGE)

        if monster is None: #no enemy found within maximum range
            return 'cancelled'
        else:
            old_ai = monster.ai
            monster.ai = creatures.ConfusedMonster(old_ai, self.CONFUSE_NUM_TURNS)
            monster.ai.owner = monster #tell the new component who owns it
            screen.message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_blue)

   
#################################################################################
# The Spell Scroll class represents items that cast spells, then disappear from 
# inventory.  It inherits both from Item and Spell.
#################################################################################
class Spell_Scroll(Item, Spell):

    def __init__(self, x, y, char, name, color, spell_name):     
        Item.__init__(self, x, y, char, name, color, use_function=None)
        #set spell name.  This is used to cast the spell.
        self.spell_name = spell_name

    
    def use(self, screen, map):                  
        #Gets the appropriate cast method based on the spell name.
        if getattr(self, 'cast_' + self.spell_name)(screen, map) != 'cancelled':
            self.owner.inventory.remove(self)


