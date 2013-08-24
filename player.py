from object import Object

__author__ = 'Steven'

class Player(Object):

    def __init__(self, object, base_character):
        self.base_object = object
        self.base_character = base_character

    def get_instance(self):
        return self.base_object

    def move_or_attack(self, dx, dy):

        #the coordinates the player is moving to/attacking
        x = self.x + dx
        y = self.y + dy

        #try to find an attackable object there
        target = None
        for object in objects:
            if object.fighter and object.x == x and object.y == y:
                target = object
                break

        #attack if target found, move otherwise
        if target is not None:
            player.fighter.attack(target)
            return False
        else:
            player.move(dx, dy)
            return True

    @property
    def object(self):
        return self.base_object