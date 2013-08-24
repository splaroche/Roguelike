import libtcodpy as libtcod
# A creature class. A creature is defined as anything that is alive, like Monsters or the Player.


####################################################################################################
# Death Methods
####################################################################################################
def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be attacked and doesn't move
    message(monster.name.capitalize() + ' is dead! You gain ' + str(monster.fighter.xp) + ' experience points!',
            libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'Remains of ' + monster.name
    monster.send_to_back()


def player_death(player):
    #the game ended!
    global game_state
    message('You died!', libtcod.red)
    game_state = 'dead'

    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red