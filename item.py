import libtcodpy as libtcod
from menu import Menu
from player import Player
from screen import Screen

__author__ = 'Steven'

class Item:

    def __init__(self, use_function=None):
        self.use_function = use_function

    def drop(self):
        #add to the map and remove from the player's inventory.  also, place it at the player's coordinates
        self.objects.append(self.owner)
        self.inventory.remove(self.owner)
        self.owner.x = self.player.x
        self.owner.y = self.player.y

        #dequip equipment that is dropped
        if self.owner.equipment:
            self.owner.equipment.dequip()

        Screen.message('You dropped a ' + self.owner.name + '.', 'yellow')

    #an item that can be picked up and used
    def pick_up(self):
        #add to the player's inventory and remove from the map
        if len(self.inventory) >= 25:
            Screen.message('Your inventory is full, cannot pick up ' + self.owner.name + '.', 'red')
        else:
            self.inventory.append(self.owner)
            self.objects.remove(self.owner)
            Screen.message('You picked up a ' + self.owner.name + '!', 'green')

            #special case: automatically equip, if the corresponding equipment slot is unused
            equipment = self.owner.equipment
            if equipment and Player.get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()


    def use(self):

        #special case: if the object has the Equipment component, the 'use' action it to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        #just call the use_function if it is defined
        if self.use_function is None:
            Screen.message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                self.inventory.remove(self.owner) #destroy after use, unless it was cancelled for some reason

