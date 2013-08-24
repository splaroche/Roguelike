__author__ = 'Steven'




class Tile:
    # a tile of the map
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        #by default, if a tiles is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight

        self.explored = False
