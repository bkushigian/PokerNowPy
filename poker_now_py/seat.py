'''
seat.py

Created by PJ Gray on 5/27/20.
Adapted to Python by Ben Kushigian on 8/7/2021
Copyright © 2020 Say Goodnight Software. All rights reserved.
'''

from typing import Optional
from player import Player

class Seat:
    def __init__(self, player:Player=None,
                       summary:str='',
                       pre_flop_bet:bool = False,
                       showed_hand:Optional[str]=None,
                       stack:Optional[float]=None,
                       number:int = 0):
        self.player: Optional[Player] = player
        self.summary: str = summary
        self.pre_flop_bet: bool = pre_flop_bet
        self.showed_hand: Optional[str] = showed_hand
        self.stack: Optional[float] = stack
        self.number: int = number
