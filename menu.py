import libtcodpy as libtcod
from screen import Screen


class Menu:

    #Constants
    #Item Menu Constants
    INVENTORY_WIDTH = 50

    def __init__(self, inventory, con):
        self.inventory = inventory
        self.con = con

    @staticmethod
    def menu(con, header, options, width):
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

    @staticmethod
    def inventory_menu(inventory, header):
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

        index = Menu.menu(header, options, Menu.INVENTORY_WIDTH)

        #if an item was chosen, return it
        if index is None or len(inventory) == 0: return None
        return inventory[index].item

    @staticmethod
    def main_menu():
        img = libtcod.image_load('menu_background.png')
        game = Game()
        while not libtcod.console_is_window_closed():
            #show the background image, at twice the regular console resolution
            libtcod.image_blit_2x(img, 0, 0, 0)

            #show the game's title and some credits!
            libtcod.console_set_default_foreground(0, libtcod.light_yellow)
            libtcod.console_print_ex(0, Screen.SCREEN_WIDTH / 2, Screen.SCREEN_HEIGHT / 2 - 4, libtcod.BKGND_NONE, libtcod.CENTER,
                                     'TOMBS OF THE ANCIENT KINGS')
            libtcod.console_print_ex(0, Screen.SCREEN_WIDTH / 2, Screen.SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER,
                                     'By Steven')

            #show options and wait for the player's choice
            choice = Menu.menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

            if choice == 0: #new game
                new_game()
                play_game()
            elif choice == 1:
                print('Huzah!')
                try:
                    load_game()
                except:
                    Menu.msgbox('\n No saved game to load!\n', 24)
                    continue
                play_game()
            elif choice == 2: #quit
                break

    @staticmethod
    def msgbox(text, width=50):
        Menu.menu(text, [], width)
