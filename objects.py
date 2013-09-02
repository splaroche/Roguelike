import libtcodpy as libtcod
import math
#################################################################################
# The Object object represents anything that might appear on the map, like items,
# player, monsters, etc.  It is usually inherited by other classes.
# NOTE:  This class is not in the map module because doing so caused circular 
#        imports with the classes that inherit it.
#################################################################################
class Object:
    def __init__(self, x, y, char, name, color, blocks=False, always_visible=False):
        self.always_visible = always_visible
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color       

    #Determines the distance between the object and some point on the map.
    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
    
    #Determines the distance between the object and another object.
    def distance_to(self, other):
        #return the distance to another object.
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    #Moves the object into the new coordinates, assuming the spot isn't blocked.
    def move(self, dx, dy, map):
        if not map.is_blocked(self.x + dx, self.y + dy):
            #move the object
            self.x += dx
            self.y += dy

    #Moves the object towards the target point, assuming the path doesn't hit a blocked square.
    def move_towards(self, target_x, target_y, map):        
        #vector from this object to the target and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #normalize it to length 1 (preserving direction), then round it and
        #convert it to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        
        self.move(dx, dy, map)

    #Draws the object on the map, assuming it's in a visible or explored square.
    def draw(self, fov_map, con, map):
        if (libtcod.map_is_in_fov(fov_map, self.x, self.y)) or (self.always_visible and map.map[self.x][self.y].explored):
        #set the color and then draw the character that represents the object
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    #Clears the object from the map and screen.
    def clear(self, con):
        #erase the char that represents the object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    #Sends the object to the back of the screen, so that other things will be drawn atop it.
    def send_to_back(self, objects):
        #make this object be drawn first, so all others appear above it if they're in the same tile
        objects.remove(self)
        objects.insert(0, self)

