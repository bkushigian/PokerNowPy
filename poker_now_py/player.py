'''
player.py

Created by PJ Gray on 5/27/20.
Adapted to Python by Ben Kushigian on 8/7/2021
Copyright © 2020 Say Goodnight Software. All rights reserved.
'''

from typing import Optional

class Player:
    def __init__(self, creator=False, admin=None, sitting=True, id=None, stack=0.0, name=None):
        self.creator: bool = creator
        self.admin: Optional[bool] = admin
        self.sitting: bool = sitting
        self.id: Optional[str] = id
        self.stack: float = stack
        self.name: Optional[str] = name
