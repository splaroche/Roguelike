import libtcodpy as libtcod
import math
class Object:
#this is a generic object: the player, a monster, etc
    def __init__(self, x, y, char, name, color, blocks=False, always_visible=False):
        self.always_visible = always_visible
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        


    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance_to(self, other):
        #return the distance to another object.
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def move(self, dx, dy, map):
        if not map.is_blocked(self.x + dx, self.y + dy):
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
        
        self.x +=dx
        self.y +=dy

    def draw(self, fov_map, con, map):
        if (libtcod.map_is_in_fov(fov_map, self.x, self.y)) or (self.always_visible and map.map[self.x][self.y].explored):
        #set the color and then draw the character that represents the object
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self, con):
        #erase the char that represents the object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def send_to_back(self, objects):
        #make this object be drawn first, so all others appear above it if they're in the same tile
        objects.remove(self)
        objects.insert(0, self)

