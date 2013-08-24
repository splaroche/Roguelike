import textwrap
import libtcodpy as libtcod

__author__ = 'Steven'


class Screen:
# Console Constants
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 50
    MAP_WIDTH = 80
    MAP_HEIGHT = 43
    LIMIT_FPS = 20

    # Menu Bar constants
    BAR_WIDTH = 20
    PANEL_HEIGHT = 7
    PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

    # Message Log Constants
    MSG_X = BAR_WIDTH + 2
    MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
    MSG_HEIGHT = PANEL_HEIGHT - 1

    # Character self Constants
    CHARACTER_SCREEN_WIDTH = 30

    # instance var
    instance = None

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

        self.fov_map = None
        self.fov_recompute = False

        self.mouse = mouse
        self.key = key

    def get_instance(self, screen=None):
        if self.instance is None:
            self.instance = screen
        return self.instance

    #########################################################################
    # Gui Section
    #########################################################################
    def message(self, game_msgs, new_msg, color='white'):
        lib_color = Screen.get_libtcod_color(color);
        #split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(new_msg, Screen.MSG_WIDTH)

        for line in new_msg_lines:
            #if the buffer is full, remove the first line to make room for the new one
            if len(game_msgs) == Screen.MSG_HEIGHT:
                del game_msgs[0]

            #add the new line as a tuple, with the text and the color
            game_msgs.append((line, lib_color))

    def render_bar(self, x, y, total_width, name, value, maximum, bar_color, back_color):
        #render a bar (HP, experience, etc). first calculate the width of the bar
        bar_width = int(float(value) / maximum * total_width)

        #render the background first
        libtcod.console_set_default_background(self.panel, back_color)
        libtcod.console_rect(self.panel, x, y, total_width, 1, False, libtcod.BKGND_self)

        #now render the bar on top
        libtcod.console_set_default_background(self.panel, bar_color)
        if bar_width > 0:
            libtcod.console_rect(self.panel, x, y, bar_width, 1, False, libtcod.BKGND_self)

        #finally, some centered text with the values
        libtcod.console_set_default_foreground(self.panel, libtcod.white)
        libtcod.console_print_ex(self.panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                                 name + ': ' + str(value) + '/' + str(maximum))

    def render_all(self, objects, map, dungeon_level):

        if self.fov_recompute:
            #recompute FOV if needed (the player moved or something)
            fov_recompute = False
            libtcod.map_compute_fov(self.fov_map, self.player.x, self.player.y, self.TORCH_RADIUS,
                                    self.FOV_LIGHT_WALLS, self.FOV_ALGO)

        #go through all the tiles and set the background color
        for y in range(self.MAP_HEIGHT):
            for x in range(self.MAP_WIDTH):
                visible = libtcod.map_is_in_fov(self.fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    if map[x][y].explored:

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
                    map[x][y].explored = True
                    #draw all objects in the list
        for object in objects:
            if object != Player.get_instance():
                object.draw()
            Player.get_instance().draw()

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
        self.render_bar(1, 1, self.BAR_WIDTH, 'HP', Player.get_instance().hp, Player.max_hp,
                        libtcod.light_red, libtcod.darker_red)

        #display the dungeon level
        libtcod.console_print_ex(self.panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT,
                                 'Dungeon Level ' + str(dungeon_level))

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

        names = ', '.join(names) #join the names, separated by commas
        return names.capitalize()

    #########################################################################
    # Input Section
    #########################################################################
    def handle_keys(self):
        key = self.key
        if key.vk == libtcod.KEY_ENTER and key.lalt:
            libtcod.console_set_fullself(not libtcod.console_is_fullself())
        elif key.vk == libtcod.KEY_ESCAPE:
            return 'exit' #exit game

        if self.game_state == 'playing':
            #movement keys
            if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
                self.player.move_or_attack(0, -1)
            elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
                self.player.move_or_attack(0, 1)
            elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
                self.player.move_or_attack(-1, 0)
            elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
                self.player.move_or_attack(1, 0)
            elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
                self.player.move_or_attack(-1, -1)
            elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
                self.player.move_or_attack(1, -1)
            elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
                self.player.move_or_attack(-1, 1)
            elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
                self.player.move_or_attack(1, 1)
            elif key.vk == libtcod.KEY_KP5:
                pass  #do nothing ie wait for the monster to come to you
            else:
                #test for other keys
                key_char = chr(key.c)
                if key_char == 'd':
                    #show the inventory; if an item is selected, drop it
                    chosen_item = self.menu.inventory_menu(
                        'Press the key next to an item to use it, or any other to cancel.\n')
                    if chosen_item is not None:
                        chosen_item.drop()

                if key_char == 'g':
                    #pick up an item
                    for object in self.objects:
                        if object.x == self.player.x and object.y == self.player.y and object.item:
                            object.item.pick_up()
                            break
                if key_char == 'i':
                    #show the inventory
                    chosen_item = self.menu.inventory_menu(
                        'Press the key next to an item to use it, or any other to cancel.\n')
                    if chosen_item is not None:
                        chosen_item.use()

                if key_char == '<' or key_char == ',':
                    #go down the stairs, if the player is on them
                    if self.stairs.x == self.player.x and self.stairs.y == self.player.y:
                        self.map.next_level()

                if key_char == 'c':
                    #show character information
                    level_up_xp = Base_Character.LEVEL_UP_BASE + self.player.level * Base_Character.LEVEL_UP_FACTOR
                    Menu.msgbox('Character Information\n\nLevel: ' + str(self.player.level) + '\nExperience: ' + str(
                        self.player.fighter.xp) + '\nExperience to level up: ' + str(
                        level_up_xp) + '\n\nMaximum HP: ' + str(
                        self.player.fighter.max_hp) + '\nAttack: ' + str(
                        self.player.fighter.power) + '\nDefense: ' + str(
                        self.player.fighter.defense), self.CHARACTER_SCREEN_WIDTH)

                return 'didnt-take-turn'

    def target_tile(self, max_range=None):
        #return the position of a tile left-clicked in player's FOV (optionally a range), or (None, None) if right-clicked
        key = self.key
        mouse = self.mouse
        while True:
            #render the self.  this erases the inventory and show the name of objects under the mouse
            libtcod.console_flush()
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
            self.render_all()

            (x, y) = (mouse.cx, mouse.cy)

            if mouse.lbutton_pressed and libtcod.map_is_in_fov(self.fov_map, x, y) and (
                        max_range is None or self.player.distance(x, y) <= max_range):
                return x, y

            if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
                return None, None #cancel if the player right-clicked or pressed Escape


    def target_monster(self, max_range=None):
        #returns a clicked monster inside FOV up to a range, or None if right-clicked
        while True:
            (x, y) = self.target_tile(max_range)
            if x is None: #player cancelled
                return None

            for obj in self.objects:
                if obj.x == x and obj.y == y and obj.fighter and obj != self.player:
                    return obj


    @staticmethod
    def get_libtcod_color(color):
        return {
            'dark_blue': libtcod.dark_blue,
            'dark_orange': libtcod.dark_orange,
            'darker_green': libtcod.darker_green,
            'desaturated_green': libtcod.desaturated_green,
            'green': libtcod.green,
            'light_blue': libtcod.light_blue,
            'light_cyan': libtcod.light_cyan,
            'light_green': libtcod.light_green,
            'light_violet': libtcod.light_violet,
            'light_yellow': libtcod.light_yellow,
            'orange': libtcod.orange,
            'sky': libtcod.sky,
            'red': libtcod.red,
            'violet': libtcod.violet,
            'yellow': libtcod.yellow
        }.get(color, libtcod.white)


    #Constants
    #Item Menu Constants
    INVENTORY_WIDTH = 50

    def menu(self, header, options, width):
        #check to see if there's more than 26 options
        if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options')

        #calculate the total height for the header (after auto-wrap) and one line per option
        if header == '':
            header_height = 0
        else:
            header_height = libtcod.console_get_height_rect(con, 0, 0, width, Screen.SCREEN_HEIGHT, header)

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

    
    def inventory_menu(self, inventory, header):
        #show a menu with each item of the inventory as an option
        if len(inventory) == 0:
            options = ['Inventory is empty!']
        else:
            options = []
            for item in inventory:
                text = item.name
                #show additional information, in case it is equipped.
                if item.equipment and item.equipment.is_equipped:
                    text = text + ' (on ' + item.equipment.slot + ')'
                options.append(text)

        index = self.menu(header, options, Menu.INVENTORY_WIDTH)

        #if an item was chosen, return it
        if index is None or len(inventory) == 0: return None
        return inventory[index].item
    
    def msgbox(self, text, width=50):
        self.menu(text, [], width)