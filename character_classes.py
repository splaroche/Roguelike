#################################################################################
# The character_classes module contains character class classes.
#################################################################################


#################################################################################
# The BaseCharacterClass represents the most basic character class possible, 
# with no extra features like spells.
#################################################################################
class BaseCharacterClass:
    #Base Leveling Constants
    LEVEL_UP_BASE = 200
    LEVEL_UP_FACTOR = 150
    LEVEL_SCREEN_WIDTH = 40

    def __init__(self, hp, defense, power, screen=None):      
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power        
        self.screen = screen        
        self.level = 1        
      
    #Total Power property, including equipment bonuses.
    @property
    def power(self):
        bonus = sum(equipment.power_bonus for equipment in self.owner.get_all_equipped())
        return self.base_power + bonus

    #Total Defense property, including equipment bonuses.
    @property
    def defense(self):
        bonus = sum(equipment.defense_bonus for equipment in self.owner.get_all_equipped())
        return self.base_defense + bonus

    #Total HP property, including equipment bonuses.
    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for equipment in self.owner.get_all_equipped())
        return self.base_max_hp + bonus

    #Default attack method.
    def attack(self, target, objects):
        #a simple formula for attack damage
        damage = self.power - target.character_class.defense
        if damage > 0:
            #make the target take some damage
            target.take_damage(damage, objects)
            self.screen.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
        else:
            self.screen.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
  