import libtcodpy as libtcod
import gui
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

    def toggle_equip(self): #toggle equip/dequip status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        #if the slot is already being used, dequip whatever is there first
        old_equipment = self.owner.get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()

        #equip object and show a message about it
        self.is_equipped = True
        gui.Screen.get_instance().message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)

    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped: return
        self.is_equipped = False
        gui.Screen.get_instance().message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)



class Item(Object):

    def __init__(self, x, y, char, name, color, use_function=None):
        Object.__init__(self, x, y, char, name, color, blocks=False, always_visible=False)
        self.use_function = use_function        

    def drop(self):
        #add to the map and remove from the player's inventory.  also, place it at the player's coordinates
        self.objects.append(self.owner)
        self.owner.inventory.remove(self.owner)
        self.owner.x = self.player.x
        self.owner.y = self.player.y

        #dequip equipment that is dropped
        if self.owner.equipment:
            self.owner.equipment.dequip()

        gui.Screen.get_instance().message('You dropped a ' + self.owner.name + '.', 'yellow')

    #an item that can be picked up and used
    def pick_up(self):
        #add to the player's inventory and remove from the map
        if len(self.inventory) >= 25:
            Screen.get_instance().message('Your inventory is full, cannot pick up ' + self.owner.name + '.', 'red')
        else:
            self.inventory.append(self.owner)
            self.objects.remove(self.owner)
            gui.Screen.get_instance().message('You picked up a ' + self.owner.name + '!', 'green')

            #special case: automatically equip, if the corresponding equipment slot is unused
            equipment = self.owner.equipment
            if equipment and Player.get_instance().get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()


    def use(self):

        #special case: if the object has the Equipment component, the 'use' action it to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        #just call the use_function if it is defined
        if self.use_function is None:
            Screen.get_instance().message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function(self) != 'cancelled':
                self.inventory.remove(self.owner) #destroy after use, unless it was cancelled for some reason



class Spell_Scroll(Item):

    def __init__(self, use_function, spell):        
        Item.__init__(self, use_function)
        self.spell = spell

    def use(self):
        if self.use_function(self) != 'cancelled':
            self.owner.inventory.remove(self.owner)


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
    def cast_fireball(self):
        #ask the player for a target tile to throw a fireball at
        Screen.get_instance().message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
        (x, y) = screen.target_tile()
        Screen.get_instance().message('The fireball explodes, burning everything within ' + str(self.FIREBALL_RADIUS) + ' tiles!', libtcod.orange)

        for obj in self.objects: #damage every fighter in range, including the player
            if obj.distance(x, y) <= self.FIREBALL_RADIUS and obj.class_name:
                Screen.get_instance().message('The ' + obj.name + ' gets burned for ' + str(self.FIREBALL_DAMAGE) + ' hit points!', libtcod.orange)
                obj.character_class.take_damage(self.FIREBALL_DAMAGE)


    def cast_heal(self):
        #heal the player
        if Player.get_instance().character_class.hp == Player.get_instance().character_class.max_hp:
            Screen.get_instance().message('You are already at full health!', libtcod.red)
            return 'cancelled'

        Screen.get_instance().message('Your wounds start to feel better!', libtcod.light_violet)
        Player.get_instance().class_name.heal_self(self.HEAL_AMOUNT)


    def cast_lightning(self):
        #find closest enemy (inside a maximum range) and damage it
        monster = self.closest_monster(self.LIGHTNING_RANGE)
        if monster is None: #no enemy found within maximum range
            Screen.get_instance().message('No enemy is close enough to strike.', libtcod.red)
            return 'cancelled'

        #zap it!
        Screen.get_instance().message('A lightning bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
                + str(self.LIGHTNING_DAMAGE) + ' hit points!', libtcod.light_blue)
        monster.character_class.take_damage(self.LIGHTNING_DAMAGE)


    def cast_confusion(self):
        #ask the player for a target to confuse
        Screen.get_instance().message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
        monster = Screen.get_instance().target_monster(self.CONFUSE_RANGE)

        if monster is None: #no enemy found within maximum range
            return 'cancelled'
        else:
            old_ai = monster.ai
            monster.ai = ConfusedMonster(old_ai, self.CONFUSE_NUM_TURNS)
            monster.ai.owner = monster #tell the new component who owns it
            Screen.get_instance().message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_blue)


    def closest_monster(self, max_range, objects):
        #find closest enemy, up to a maximum range, and in the player's FOV
        closest_enemy = None
        closest_dist = max_range + 1 #start with (slightly more than) maximum range

        for object in self.objects:
            if object is Creature and not object == Player.get_instance() and libtcod.map_is_in_fov(fov_map, object.x, object.y):
                #calculate distance between this object and the player
                dist = Player.get_instance().distance_to(object)
                if dist < closest_dist: #it's closer, so remember it
                    closest_enemy = object
                    closest_dist = dist
        return closest_enemy



