import random
import unittest
import game, map, creatures, gui, character_classes

class MapTestFunctions(unittest.TestCase):
    def test_change_map_level(self):
        game_map = map.GameMap()
        fighter_component = character_classes.BaseCharacterClass(hp=100, defense=1, power=4)       
        game_map.player = creatures.Player(game_map.orig_player_x, game_map.orig_player_y, '@', 'player', '', blocks=True, character_class=fighter_component, screen=None)
        game_map.screen = gui.Screen()
        game_map.make()
        game_map.next_level()
        self.assertGreaterEqual(game_map.levels, 2, 'Check that map levels are generated.')

    def test_create_stairs(self):        
        game_map = map.GameMap()
        fighter_component = character_classes.BaseCharacterClass(hp=100, defense=1, power=4)       
        game_map.player = creatures.Player(game_map.orig_player_x, game_map.orig_player_y, '@', 'player', '', blocks=True, character_class=fighter_component, screen=None)
        game_map.screen = gui.Screen()
        game_map.make()
        game_map.next_level()
        
        print game_map.dungeon_level
        print len(game_map.stairs)
        for i in game_map.stairs:
            print i.char
        self.assertEqual(game_map.stairs, 3, 'Check that stairs have been created down on level 1, and up/down on level 2')
        game_map.next_level()
        self.assertEqual(game_map.stairs, 5, 'Check that stairs have been created down on level 1, and up/down on level 2, and up/down on level 3')
        
        
class GameTestFunctions(unittest.TestCase):
    def test_player_respawn(self):
        g = game.Game()
        g.new_game()
        g.map.next_level()
        g.map.next_level()
        g.respawn_player()
        
        self.assertEquals((g.map.player.x, g.map.player.y), (g.map.orig_player_x, g.map.orig_player_y) , 'Check the player moves back to start.')
        self.assertEquals(g.map.dungeon_level, 1 , 'Check the dungeon level is back to 1.')
        self.assertGreaterEqual(g.map.levels, 3, 'Check that map levels are still generated.')
    
    
if __name__ == '__main__':
    unittest.main()