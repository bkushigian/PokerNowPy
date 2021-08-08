'''
card.py

Created by PJ Gray on 5/27/20.
Adapted to Python by Ben Kushigian on 8/7/2021
Copyright © 2020 Say Goodnight Software. All rights reserved.
'''

from enum import Enum, unique

@unique
class EmojiCard(Enum):
    c2 = "2♣"
    c3 = "3♣"
    c4 = "4♣"
    c5 = "5♣"
    c6 = "6♣"
    c7 = "7♣"
    c8 = "8♣"
    c9 = "9♣"
    cT = "10♣"
    cJ = "J♣"
    cQ = "Q♣"
    cK = "K♣"
    cA = "A♣"

    d2 = "2♦"
    d3 = "3♦"
    d4 = "4♦"
    d5 = "5♦"
    d6 = "6♦"
    d7 = "7♦"
    d8 = "8♦"
    d9 = "9♦"
    dT = "10♦"
    dJ = "J♦"
    dQ = "Q♦"
    dK = "K♦"
    dA = "A♦"

    h2 = "2♥"
    h3 = "3♥"
    h4 = "4♥"
    h5 = "5♥"
    h6 = "6♥"
    h7 = "7♥"
    h8 = "8♥"
    h9 = "9♥"
    hT = "10♥"
    hJ = "J♥"
    hQ = "Q♥"
    hK = "K♥"
    hA = "A♥"

    s2 = "2♠"
    s3 = "3♠"
    s4 = "4♠"
    s5 = "5♠"
    s6 = "6♠"
    s7 = "7♠"
    s8 = "8♠"
    s9 = "9♠"
    sT = "10♠"
    sJ = "J♠"
    sQ = "Q♠"
    sK = "K♠"
    sA = "A♠"

    error = "Error"
    
    def emojiFlip(self):
        if self == EmojiCard.c2: return Card.c2
        elif self == EmojiCard.c3: return Card.c3
        elif self == EmojiCard.c4: return Card.c4
        elif self == EmojiCard.c5: return Card.c5
        elif self == EmojiCard.c6: return Card.c6
        elif self == EmojiCard.c7: return Card.c7
        elif self == EmojiCard.c8: return Card.c8
        elif self == EmojiCard.c9: return Card.c9
        elif self == EmojiCard.cT: return Card.cT
        elif self == EmojiCard.cJ: return Card.cJ
        elif self == EmojiCard.cQ: return Card.cQ
        elif self == EmojiCard.cK: return Card.cK
        elif self == EmojiCard.cA: return Card.cA

        elif self == EmojiCard.d2: return Card.d2
        elif self == EmojiCard.d3: return Card.d3
        elif self == EmojiCard.d4: return Card.d4
        elif self == EmojiCard.d5: return Card.d5
        elif self == EmojiCard.d6: return Card.d6
        elif self == EmojiCard.d7: return Card.d7
        elif self == EmojiCard.d8: return Card.d8
        elif self == EmojiCard.d9: return Card.d9
        elif self == EmojiCard.dT: return Card.dT
        elif self == EmojiCard.dJ: return Card.dJ
        elif self == EmojiCard.dQ: return Card.dQ
        elif self == EmojiCard.dK: return Card.dK
        elif self == EmojiCard.dA: return Card.dA

        elif self == EmojiCard.h2: return Card.h2
        elif self == EmojiCard.h3: return Card.h3
        elif self == EmojiCard.h4: return Card.h4
        elif self == EmojiCard.h5: return Card.h5
        elif self == EmojiCard.h6: return Card.h6
        elif self == EmojiCard.h7: return Card.h7
        elif self == EmojiCard.h8: return Card.h8
        elif self == EmojiCard.h9: return Card.h9
        elif self == EmojiCard.hT: return Card.hT
        elif self == EmojiCard.hJ: return Card.hJ
        elif self == EmojiCard.hQ: return Card.hQ
        elif self == EmojiCard.hK: return Card.hK
        elif self == EmojiCard.hA: return Card.hA

        elif self == EmojiCard.s2: return Card.s2
        elif self == EmojiCard.s3: return Card.s3
        elif self == EmojiCard.s4: return Card.s4
        elif self == EmojiCard.s5: return Card.s5
        elif self == EmojiCard.s6: return Card.s6
        elif self == EmojiCard.s7: return Card.s7
        elif self == EmojiCard.s8: return Card.s8
        elif self == EmojiCard.s9: return Card.s9
        elif self == EmojiCard.sT: return Card.sT
        elif self == EmojiCard.sJ: return Card.sJ
        elif self == EmojiCard.sQ: return Card.sQ
        elif self == EmojiCard.sK: return Card.sK
        elif self == EmojiCard.sA: return Card.sA
        return Card.error


class Card(Enum):
    c2 = "2c"
    c3 = "3c"
    c4 = "4c"
    c5 = "5c"
    c6 = "6c"
    c7 = "7c"
    c8 = "8c"
    c9 = "9c"
    cT = "Tc"
    cJ = "Jc"
    cQ = "Qc"
    cK = "Kc"
    cA = "Ac"

    d2 = "2d"
    d3 = "3d"
    d4 = "4d"
    d5 = "5d"
    d6 = "6d"
    d7 = "7d"
    d8 = "8d"
    d9 = "9d"
    dT = "Td"
    dJ = "Jd"
    dQ = "Qd"
    dK = "Kd"
    dA = "Ad"

    h2 = "2h"
    h3 = "3h"
    h4 = "4h"
    h5 = "5h"
    h6 = "6h"
    h7 = "7h"
    h8 = "8h"
    h9 = "9h"
    hT = "Th"
    hJ = "Jh"
    hQ = "Qh"
    hK = "Kh"
    hA = "Ah"

    s2 = "2s"
    s3 = "3s"
    s4 = "4s"
    s5 = "5s"
    s6 = "6s"
    s7 = "7s"
    s8 = "8s"
    s9 = "9s"
    sT = "Ts"
    sJ = "Js"
    sQ = "Qs"
    sK = "Ks"
    sA = "As"
    error = "Error"
