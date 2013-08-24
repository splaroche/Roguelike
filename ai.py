import libtcodpy as libtcod
from spells import Spells

__author__ = 'Steven'


class BasicMonster:
    def __init__(self, player, fov_map):
        self.fov_map = fov_map
        self.player = player

    #AI for a basic monster
    def take_turn(self):
        #a basic monster takes its turn.  If you can see it, it can see you
        monster = self.owner
        if libtcod.map_is_in_fov(self.fov_map, monster.x, monster.y):

            #move towards player if far away
            if monster.distance_to(self.player) >= 2:
                monster.move_towards(self.player.x, self.player.y)

            #close enough, attack! (if the player is still alive.)
            elif self.player.fighter.hp > 0:
                monster.fighter.attack(self.player)


class ConfusedMonster:
    #AI for a temporarily confused monster (reverts to previous AI after a while)
    def __init__(self, old_ai, num_turns=Spells.CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0: #still confused
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else: #restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            return ('The ' + self.owner.name + ' is no longer confused!', libtcod.red)

