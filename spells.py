from ai import ConfusedMonster
import libtcodpy as libtcod
from menu import Menu

__author__ = 'Steven'
class Spells:

    # Spell Constants
    HEAL_AMOUNT = 40
    LIGHTNING_RANGE = 5
    LIGHTNING_DAMAGE = 40
    CONFUSE_NUM_TURNS = 10
    CONFUSE_RANGE = 8
    FIREBALL_RADIUS = 3
    FIREBALL_DAMAGE = 25

    ########################################################################################
    # Spell Static Casting Methods
    ########################################################################################
    def cast_fireball(self):
        #ask the player for a target tile to throw a fireball at
        Menu.message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
        (x, y) = screen.target_tile()
        Menu.message('The fireball explodes, burning everything within ' + str(Spells.FIREBALL_RADIUS) + ' tiles!', libtcod.orange)

        for obj in objects: #damage every fighter in range, including the player
            if obj.distance(x, y) <= Spells.FIREBALL_RADIUS and obj.class_name:
                Menu.message('The ' + obj.name + ' gets burned for ' + str(Spells.FIREBALL_DAMAGE) + ' hit points!', libtcod.orange)
                obj.class_name.take_damage(Spells.FIREBALL_DAMAGE)


    def cast_heal(self):
        #heal the player
        if player.class_name.hp == player.class_name.max_hp:
            Menu.message('You are already at full health!', libtcod.red)
            return 'cancelled'

        Menu.message('Your wounds start to feel better!', libtcod.light_violet)
        player.class_name.heal_self(Spells.HEAL_AMOUNT)


    def cast_lightning(self):
        #find closest enemy (inside a maximum range) and damage it
        monster = self.closest_monster(Spells.LIGHTNING_RANGE)
        if monster is None: #no enemy found within maximum range
            Menu.message('No enemy is close enough to strike.', libtcod.red)
            return 'cancelled'

        #zap it!
        Menu.message('A lightning bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
                + str(Spells.LIGHTNING_DAMAGE) + ' hit points!', libtcod.light_blue)
        monster.class_name.take_damage(Spells.LIGHTNING_DAMAGE)


    def cast_confusion(self):
        #ask the player for a target to confuse
        Menu.message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
        monster = self.target_monster(Spells.CONFUSE_RANGE)

        if monster is None: #no enemy found within maximum range
            return 'cancelled'
        else:
            old_ai = monster.ai
            monster.ai = ConfusedMonster(old_ai)
            monster.ai.owner = monster #tell the new component who owns it
            Menu.message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_blue)



    def closest_monster(self, max_range, objects):
        #find closest enemy, up to a maximum range, and in the player's FOV
        closest_enemy = None
        closest_dist = max_range + 1 #start with (slightly more than) maximum range

        for object in objects:
            if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
                #calculate distance between this object and the player
                dist = player.distance_to(object)
                if dist < closest_dist: #it's closer, so remember it
                    closest_enemy = object
                    closest_dist = dist
        return closest_enemy


