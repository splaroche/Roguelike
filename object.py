import math
from item import Item
import libtcodpy as libtcod

__author__ = 'Steven'


class Object:
#this is a generic object: the player, a monster, etc
    def __init__(self, x, y, char, name, color, blocks=False, class_name=None, ai=None, item=None, always_visible=False,
                 equipment=None):
        self.always_visible = always_visible
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color

        self.class_name = class_name
        if self.class_name:
            # let the fighter component know who owns it
            self.class_name.owner = self

        self.ai = ai
        if self.ai:
            # let the ai component know who owns it
            self.ai.owner = self

        self.item = item
        if self.item:
            self.item.owner = self



    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance_to(self, other):
        #return the distance to another object.
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def move(self, dx, dy):
        #move the object
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y):
        #vector from this object to the target and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #normalize it to length 1 (preserving direction), then round it and
        #convert it to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def draw(self, fov_map, con):
        if (libtcod.map_is_in_fov(fov_map, self.x, self.y)) or (self.always_visible and map[self.x][self.y].explored):
        #set the color and then draw the character that represents the object
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self, con):
        #erase the char that represents the object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def send_to_back(self):
        #make this object be drawn first, so all others appear above it if they're in the same tile
        global objects
        objects.remove(self)
        objects.insert(0, self)

