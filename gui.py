###########################################################################################
# The GUI module contains any classes directly affecting screen rendering.
###########################################################################################

import textwrap, inspect
import libtcodpy as libtcod
import character_classes, items
__author__ = 'Steven'

###########################################################################################
# The Screen class represents the on screen display, including menus, map area, and consoles
# and the (re)rendering of same.
###########################################################################################
class Screen:
    #Screen and Map constants
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 50
    MAP_WIDTH = 80
    MAP_HEIGHT = 43

    #Limiter Constant (used to reduce the speed of the game to be actually turnbased.  
    #removing calls to LIMIT_FPS result in two keystrokes being recorded for every one 
    #entered.)
    LIMIT_FPS = 20

    # Menu Bar Panel constants
    BAR_WIDTH = 20
    PANEL_HEIGHT = 7
    PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

    # Message Log Constants
    MSG_X = BAR_WIDTH + 2
    MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
    MSG_HEIGHT = PANEL_HEIGHT - 1

    # Character Screen Constants
    CHARACTER_SCREEN_WIDTH = 30

    #Item Menu Constants
    INVENTORY_WIDTH = 50

    def __init__(self, mouse=None, key=None):
        # initialize the console
        # set the font, and consoles
        libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 'python/libtcod tutorial', False)
        self.con = libtcod.console_new(self.MAP_WIDTH, self.MAP_HEIGHT)
        self.panel = libtcod.console_new(self.SCREEN_WIDTH, self.PANEL_HEIGHT)
        libtcod.sys_set_fps(self.LIMIT_FPS)

        # create the tile colors
        self.color_dark_wall = libtcod.Color(0, 0, 100)
        self.color_dark_ground = libtcod.Color(50, 50, 100)
        self.color_light_wall = libtcod.Color(130, 110, 50)
        self.color_light_ground = libtcod.Color(200, 180, 50)

        # set the fov initially to None.  This will be generated properly when the map is rendered
        self.fov_map = None
        self.fov_recompute = False

        # set the mous and keyboard capture vars
        self.mouse = mouse
        self.key = key

        # set the message console
        self.game_msgs = []

    #########################################################################
    # Gui Section
    #########################################################################
    def message(self, new_msg, color=libtcod.white):        
        #split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(new_msg, self.MSG_WIDTH)

        for line in new_msg_lines:
            #if the buffer is full, remove the first line to make room for the new one
            if len(self.game_msgs) == self.MSG_HEIGHT:
                del self.game_msgs[0]

            #add the new line as a tuple, with the text and the color
            self.game_msgs.append((line, color))

    def render_bar(self, x, y, total_width, name, value, maximum, bar_color, back_color):
        #render a bar (HP, experience, etc). first calculate the width of the bar
        bar_width = int(float(value) / maximum * total_width)

        #render the background first
        libtcod.console_set_default_background(self.panel, back_color)
        libtcod.console_rect(self.panel, x, y, total_width, 1, False, libtcod.BKGND_NONE)

        #now render the bar on top
        libtcod.console_set_default_background(self.panel, bar_color)
        if bar_width > 0:
            libtcod.console_rect(self.panel, x, y, bar_width, 1, False, libtcod.BKGND_NONE)

        #finally, some centered text with the values
        libtcod.console_set_default_foreground(self.panel, libtcod.white)
        libtcod.console_print_ex(self.panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                                 name + ': ' + str(value) + '/' + str(maximum))

    def render_all(self, map):
        #render the whole screen, including the bar, fov and map
        objects = map.objects
        player = map.player

        if self.fov_recompute:
            #recompute FOV if needed (the player moved or something)
            fov_recompute = False
            libtcod.map_compute_fov(self.fov_map, player.x, player.y, map.TORCH_RADIUS,
                                    map.FOV_LIGHT_WALLS, map.FOV_ALGO)

        #go through all the tiles and set the background color
        for y in range(self.MAP_HEIGHT):
            for x in range(self.MAP_WIDTH):
                visible = libtcod.map_is_in_fov(self.fov_map, x, y)
                wall = map.map[x][y].block_sight
                if not visible:
                    if map.map[x][y].explored:

                    #it's out of the player's FOV
                        if wall:
                            libtcod.console_set_char_background(self.con, x, y, self.color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(self.con, x, y, self.color_dark_ground,
                                                                libtcod.BKGND_SET)
                else:
                    #it's visible
                    if wall:
                        libtcod.console_set_char_background(self.con, x, y, self.color_light_wall, libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(self.con, x, y, self.color_light_ground, libtcod.BKGND_SET)
                    map.map[x][y].explored = True
        
        #draw all objects in the list
        for object in objects:
            if object != player:
                object.draw(self.fov_map, self.con, map)
            # draw the player last, to ensure it ends up on top of other objects
            player.draw(self.fov_map, self.con, map)

        #blit the contents of the "con" to the root console
        libtcod.console_blit(self.con, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0, 0)

        #prepare to render the GUI panel
        libtcod.console_set_default_background(self.panel, libtcod.black)
        libtcod.console_clear(self.panel)

        #print the game messages, one line at a time
        y = 1
        for (line, color) in self.game_msgs:
            libtcod.console_set_default_foreground(self.panel, color)
            libtcod.console_print_ex(self.panel, self.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
            y += 1

        #show the player's stats
        self.render_bar(1, 1, self.BAR_WIDTH, 'HP', player.character_class.hp, player.character_class.max_hp,
                        libtcod.light_red, libtcod.darker_red)

        #display the dungeon level
        libtcod.console_print_ex(self.panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT,
                                 'Dungeon Level ' + str(map.dungeon_level))

        #display names of the objects under the mouse
        libtcod.console_set_default_background(self.panel, libtcod.light_gray)
        libtcod.console_print_ex(self.panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, self.get_names_under_mouse(objects))

        #blit the contents of "panel" to the root console
        libtcod.console_blit(self.panel, 0, 0, self.SCREEN_WIDTH, self.PANEL_HEIGHT, 0, 0, self.PANEL_Y)

    def get_names_under_mouse(self, objects):
        #return a string with the names of all objects under the mouse
        (x, y) = (self.mouse.cx, self.mouse.cy)

        #create a list with the names of all objects at the mouse's coordinates and in FOV
        names = [obj.name for obj in objects
                 if obj.x == x and obj.y == y and libtcod.map_is_in_fov(self.fov_map, obj.x, obj.y)]

        #join the names, separated by commas
        names = ', '.join(names) 
        return names.capitalize()

    #########################################################################
    # Input Section
    #########################################################################
    def handle_keys(self, game_state, player, objects, map):
        #take keyboard input and determine what to do with it
        key = self.key

        #special cases for fullscreen and quitting
        if key.vk == libtcod.KEY_ENTER and key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        elif key.vk == libtcod.KEY_ESCAPE:
            return 'exit' #exit game

        if game_state == 'playing':
            #movement keys
            if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
                player.move_or_attack(0, -1, objects, map)
            elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
                player.move_or_attack(0, 1, objects, map)
            elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
                player.move_or_attack(-1, 0, objects, map)
            elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
                player.move_or_attack(1, 0, objects, map)
            elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
                player.move_or_attack(-1, -1, objects, map)
            elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
                player.move_or_attack(1, -1, objects, map)
            elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
                player.move_or_attack(-1, 1, objects, map)
            elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
                player.move_or_attack(1, 1, objects, map)
            elif key.vk == libtcod.KEY_KP5:
                pass  #do nothing ie wait for the monster to come to you
            else:
                #test for other keys
                key_char = chr(key.c)

                if key_char == 'd':
                    #show the inventory; if an item is selected, drop it
                    chosen_item = self.inventory_menu(player.inventory,
                        'Press the key next to an item to use it, or any other to cancel.\n')
                    if chosen_item is not None:
                        player.drop_item(chosen_item, self)
                        objects.append(chosen_item)

                if key_char == 'g':
                    #pick up an item
                    for object in objects:
                        # check if the object is an item or equipment
                        if object.x == player.x and object.y == player.y and (isinstance(object, items.Item) or isinstance(object, items.Equipment)) :                            
                            # pick up the item and remove it from the objects list
                            player.pick_up_item(object, self)
                            objects.remove(object)
                            break

                if key_char == 'i':
                    #show the inventory
                    chosen_item = self.inventory_menu(player.inventory,
                        'Press the key next to an item to use it, or any other to cancel.\n')
                    if chosen_item is not None:
                        chosen_item.use(self, map)

                if key_char == '<' or key_char == ',':
                    #go down the stairs, if the player is on them
                    if map.stairs.x == player.x and map.stairs.y == player.y:
                        self.map.next_level()

                if key_char == 'c':
                    #show character information

                    # determine the player's xp progression
                    level_up_xp = character_classes.BaseCharacterClass.LEVEL_UP_BASE + player.level * character_classes.BaseCharacterClass.LEVEL_UP_FACTOR
                    self.msgbox('Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(
                        player.xp) + '\nExperience to level up: ' + str(
                        level_up_xp) + '\n\nMaximum HP: ' + str(
                        player.character_class.max_hp) + '\nAttack: ' + str(
                        player.character_class.power) + '\nDefense: ' + str(
                        player.character_class.defense), self.CHARACTER_SCREEN_WIDTH)

                # no keys pressed
                return 'didnt-take-turn'


    def target_tile(self, map, max_range=None):
        #return the position of a tile left-clicked in player's FOV (optionally a range), or (None, None) if right-clicked
        while True:
            #render the self.  this erases the inventory and show the name of objects under the mouse
            libtcod.console_flush()
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, self.key, self.mouse)
            self.render_all(map)

            (x, y) = (self.mouse.cx, self.mouse.cy)


            if self.mouse.lbutton_pressed and libtcod.map_is_in_fov(self.fov_map, x, y) and (
                        max_range is None or map.player.distance(x, y) <= max_range):
                #if the player left clicked on something, and it's within range, return the coordinates
                return x, y

            if self.mouse.rbutton_pressed or self.key.vk == libtcod.KEY_ESCAPE:
                #cancel if the player right-clicked or pressed Escape
                return None, None 

    ###############################################################################
    # Menu methods
    ###############################################################################
    def menu(self, header, options, width):
        #check to see if there's more than 26 options
        if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options')

        #calculate the total height for the header (after auto-wrap) and one line per option
        if header == '':
            header_height = 0
        else:
            header_height = libtcod.console_get_height_rect(self.con, 0, 0, width, Screen.SCREEN_HEIGHT, header)

        height = len(options) + header_height

        #create an off-screen console that represents the menu's window
        window = libtcod.console_new(width, height)

        #print the header, with auto-wrap
        libtcod.console_set_default_foreground(window, libtcod.white)
        libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

        #print all the options
        y = header_height
        letter_index = ord('a')
        for option_text in options:
            text = '(' + chr(letter_index) + ') ' + option_text
            libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
            y += 1
            letter_index += 1

        #blit the contents of the 'window' to the root console
        x = Screen.SCREEN_WIDTH / 2 - width / 2
        y = Screen.SCREEN_HEIGHT / 2 - height / 2
        libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

        #present the root console to the player and wait for a key-press
        libtcod.console_flush()
        key = libtcod.console_wait_for_keypress(True)

        #check if they user wants to go full screen
        if key.vk == libtcod.KEY_ENTER and key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        #convert the ASCII code to an index; if it corresponds to an option, return it
        index = key.c - ord('a')
        if index >= 0 and index < len(options): return index
        return None

    
    def inventory_menu(self, inventory, header=''):
        #show a menu with each item of the inventory as an option
        if len(inventory) == 0:
            options = ['Inventory is empty!']
        else:
            options = []
            for item in inventory:
                text = item.name
                #show additional information, in case it is equipped.
                #if item.equipment and item.equipment.is_equipped:
                #    text = text + ' (on ' + item.equipment.slot + ')'
                options.append(text)

        index = self.menu(header, options, self.INVENTORY_WIDTH)

        #if an item was chosen, return it
        if index is None or len(inventory) == 0: return None
        
        return inventory[index]
    
    def msgbox(self, text, width=50):
        # send a message to the menu to display it as a popup on screen
        self.menu(text, [], width)