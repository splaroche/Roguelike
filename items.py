import libtcodpy as libtcod
import gui, creatures
from objects import Object
__author__ = 'Steven'

class Equipment(Object):

    
    #an object that can be equipped, yielding bonuses.  automatically adds the Item component.
    def __init__(self, x, y, char, name, color, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        Object.__init__(self, x, y, char, name, color, blocks=False, always_visible=False)        
        self.slot = slot
        self.is_equipped = False
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus

    #equip or dequip an item
    def toggle_equip(self): #toggle equip/dequip status
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



class Item(Object):

    def __init__(self, x, y, char, name, color, use_function=None):
        Object.__init__(self, x, y, char, name, color, blocks=False, always_visible=False)
        self.use_function = use_function        

  
    def use(self, screen, map=None):

        #special case: if the object has the Equipment component, the 'use' action it to equip/dequip
        if isinstance(self, Equipment) and self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        #just call the use_function if it is defined
        if self.use_function is None:
            screen.message('The ' + self.name + ' cannot be used.')
        else:
            if self.use_function(screen, map) != 'cancelled':
                self.owner.inventory.remove(self) #destroy after use, unless it was cancelled for some reason

class Spell:

    # Spell Constants
    HEAL_AMOUNT = 40
    LIGHTNING_RANGE = 5
    LIGHTNING_DAMAGE = 40
    CONFUSE_NUM_TURNS = 10
    CONFUSE_NUM_TURNS = 10
    CONFUSE_RANGE = 8
    FIREBALL_RADIUS = 3
    FIREBALL_DAMAGE = 25

    def __init__(self, objects):
        self.objects = objects

    ########################################################################################
    # Spell Static Casting Methods
    ########################################################################################
    def cast_fireball(self, screen, map):
        #ask the player for a target tile to throw a fireball at
        screen.message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
        (x, y) = screen.target_tile(map)
        screen.message('The fireball explodes, burning everything within ' + str(self.FIREBALL_RADIUS) + ' tiles!', libtcod.orange)
        
        for obj in map.objects: #damage every fighter in range, including the player
            if isinstance(obj, creatures.Creature) and obj.distance(x, y) <= self.FIREBALL_RADIUS:
                screen.message('The ' + obj.name + ' gets burned for ' + str(self.FIREBALL_DAMAGE) + ' hit points!', libtcod.orange)                
                obj.character_class.take_damage(self.LIGHTNING_DAMAGE, map.objects)


    def cast_heal(self, screen, map):
        #heal the player
        if self.owner.character_class.hp == self.owner.character_class.max_hp:
            screen.message('You are already at full health!', libtcod.red)
            return 'cancelled'

        screen.message('Your wounds start to feel better!', libtcod.light_violet)
        self.owner.character_class.heal_self(self.HEAL_AMOUNT)


    def cast_lightning(self, screen, map):
        #find closest enemy (inside a maximum range) and damage it
        monster = self.closest_monster(self.LIGHTNING_RANGE, map.objects, screen)
        if monster is None: #no enemy found within maximum range
            screen.message('No enemy is close enough to strike.', libtcod.red)
            return 'cancelled'
        #zap it!
        screen.message('A lightning bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
                + str(self.LIGHTNING_DAMAGE) + ' hit points!', libtcod.light_blue)
        monster.character_class.take_damage(self.LIGHTNING_DAMAGE, map.objects)


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


    def closest_monster(self, max_range, objects, screen):
        #find closest enemy, up to a maximum range, and in the player's FOV
        closest_enemy = None
        closest_dist = max_range + 1 #start with (slightly more than) maximum range

        for object in objects:
            if isinstance(object,creatures.Creature) and not object == self.owner and libtcod.map_is_in_fov(screen.fov_map, object.x, object.y):
                #calculate distance between this object and the player
                dist = self.owner.distance_to(object)
                if dist < closest_dist: #it's closer, so remember it
                    closest_enemy = object
                    closest_dist = dist
        return closest_enemy





class Spell_Scroll(Item, Spell):

    def __init__(self, x, y, char, name, color, spell_name):     
        Item.__init__(self, x, y, char, name, color, use_function=None)
        self.spell_name = spell_name

    
    def use(self, screen, map):                  
        if getattr(self, 'cast_' + self.spell_name)(screen, map) != 'cancelled':
            self.owner.inventory.remove(self)


