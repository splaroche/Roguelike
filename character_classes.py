from items import Item



class BaseCharacterClass:
    #Leveling Constants
    LEVEL_UP_BASE = 200
    LEVEL_UP_FACTOR = 150
    LEVEL_SCREEN_WIDTH = 40

    #combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power):      
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power        

      
    @property
    def power(self):
        bonus = sum(equipment.power_bonus for equipment in self.get_all_equipped(self.owner))
        return self.base_power + bonus

    @property
    def defense(self):
        bonus = sum(equipment.defense_bonus for equipment in self.get_all_equipped(self.owner))
        return self.base_defense + bonus

    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for equipment in self.get_all_equipped(self.owner))
        return self.base_power + bonus

    def attack(self, target, screen):
        #a simple formula for attack damage
        damage = self.power - target.fighter.defense

        if damage > 0:
            #make the target take some damage
            target.fighter.take_damage(damage)
            screen.menu(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.',
                    'white')
        else:
            screen.menu(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!',
                    'white')

    def heal_self(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def take_damage(self, damage):
        #apply damage if possible
        if damage > 0:
            self.hp -= damage

        #check for death.  if there's a death function call it
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)

         #yield experience to the player
        Player.get_instance().xp += self.xp

    ##########################################################################################
    # Leveling Functions
    ##########################################################################################
    # check the level if the object is the player
    def check_level_up(self, screen):
        if self.owner.name == 'player':
            player = self.owner
            #see if the player's experience is enough to level-up
            level_up_xp = self.LEVEL_UP_BASE + player.level + self.LEVEL_UP_FACTOR
            if player.xp >= level_up_xp:
                #it is! level up
                player.level += 1
                player.xp -= level_up_xp
                screen.menu('Your battle skills grow stronger! You reached level ' + str(player.level) + '!', 'yellow')

                choice = None
                while choice is None: #keep asking until a choice is made
                    choice = screen.menu('Level up! Choose a stat to raise:\n',
                                       ['Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')',
                                        'Strength (+1 attack, from ' + str(player.fighter.power) + ')',
                                        'Agility (+1 defense, from ' + str(player.fighter.defense) + ')'],
                                       self.LEVEL_SCREEN_WIDTH)

                if choice == 0:
                    self.base_max_hp += 20
                    self.hp += 20
                elif choice == 1:
                    self.base_power += 1
                elif choice == 2:
                    self.base_defense += 1

    def get_equipped_in_slot(self, slot): # returns the equipment in a slot, or None if it's empty
        for obj in self.equipment:
            if obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj.equipment
        return None

    def get_all_equipped(self, owner):  #returns a list of equipped items
        if owner.name == 'player':
            equipped_list = []
            for item in owner.equipment:
                if item.is_equipped:
                    equipped_list.append(item.equipment)
            return equipped_list
        else:
            return []  #other objects have no equipment
