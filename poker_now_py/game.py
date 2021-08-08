'''
game.py

Created by PJ Gray on 5/27/20.
Adapted to Python by Ben Kushigian on 8/7/2021
Copyright © 2020 Say Goodnight Software. All rights reserved.
'''

from typing import List, Optional, Dict
from util import nil_guard, first, last, hash_str_as_id
from datetime import datetime

from player import Player
from hand import Hand
from card import EmojiCard
from seat import Seat

class Game:

    def __init__(self):
    
        self.debugHandAction: bool = False
        self.showErrors: bool = True
        self.hands: List[Hand] = []
        self.currentHand: Optional[Hand] = None

        self.dealerId: Optional[str] = None

    def init(self, rows: List[Dict[str,str]]):
        # super.init()

        last_row = last(rows)
        at = last_row["at"] if last_row else None
        if self.isSupportedLog(at=at):
            for row in rows[::-1]:
                self.parseLine(msg=row["entry"], at=row["at"], order=row["order"])
        else:
            print("Unsupported log format: the PokerNow.club file format has changed since this log was generated")
        
    def isSupportedLog(at: str) -> bool:
        format_str = "%Y-%m-%d'T'%H:%M:%S:%f%z"   # from Swift format string "yyyy-MM-dd'T'HH:mm:ss.SSSZ"

        try:
            date = datetime.strptime(date_string=nil_guard(at, ""), format=format_str)
        except:
            raise RuntimeError("Cannot parse log's date")
            
        oldestSupportedLog = datetime.fromtimestamp(1594731595)
        
        return date > oldestSupportedLog
    
    def parseLine(self, msg: Optional[str], at: Optional[str], order: Optional[str]):
        format_str = "%Y-%m-%d'T'%H:%M:%S:%f%z"   # from Swift format string "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
        date = datetime.strptime(at, format_str) if at else datetime.strptime("")
        
        if msg and msg.startswith("-- starting hand "):
            startingHandComponents = msg.split(' (dealer: "')
            unparsedDealer = last(startingHandComponents).replace('") --', "")
            
            # for legacy logs
            dealerSeparator = " @ "
            if unparsedDealer and unparsedDealer.contains(" # "):
                dealerSeparator = " # "

            hand = Hand()
            if msg.contains("dead button"):
                hand.id = hash_str_as_id(f"deadbutton-{date.timestamp() if date else 0}")
                hand.dealer = None
            else:
                dealerNameIdArray = unparsedDealer and unparsedDealer.split(dealerSeparator)
                self.dealerId = dealerNameIdArray and last(dealerNameIdArray)
                hand.id = hash_str_as_id(f"{nil_guard(self.dealerId, 'error')}-{date.timestamp() if date else 0}")
                
            hand.date = date
            self.currentHand = hand
            self.hands.append(hand)
        elif msg and msg.startswith("-- ending hand "):
            if self.debugHandAction:
                print("----")
        elif msg and msg.startswith("Player stacks"):
            playersWithStacks = msg.replace("Player stacks: ", "").split(" | ")
            players : List[Player] = []
            
            for playerWithStack in nil_guard(playersWithStacks, []):
                seatNumber = first(playerWithStack.split(" "))
                playerWithStackNoSeat = playerWithStack.replace(f"{nil_guard(seatNumber, '')} ", "")
                seatNumberInt = int(seatNumber.replace("#", "") if seatNumber is not None else "0")
                
                nameIdArray = first(playerWithStackNoSeat.split('\" '))
                nameIdArray = nameIdArray and nameIdArray.replace('"', "").split(" @ ")
                stackSize = last(playerWithStack.split('" (')).replace(")", "")
                
                player = Player(admin=False, id=last(nameIdArray), stack=float(nil_guard(stackSize, "0")), name=first(nameIdArray))
                players.append(player)
                
                self.currentHand and self.currentHand.seats.append(Seat(player=player, summary=f"{nil_guard(player.name, 'Unknown')} didn't show and lost", preFlopBet=False, number=seatNumberInt))
                        
            self.currentHand.players = players
            dealer = first([x for x in players if x.id == self.dealerId])
            if dealer:
                self.currentHand.dealer = dealer
        elif msg and msg.startswith("Your hand is "):
            self.currentHand.hole = [EmojiCard(c.strip()).value for c in  msg.replace("Your hand is ", "").split(", ")]

            if self.debugHandAction:
                print(f"#{nil_guard(self.currentHand.id, 0)} - hole cards: {[c.value for c in nil_guard(self.currentHand.hole, [])]}")
        elif msg and msg.startswith("flop"):
            line = slice(msg, start='[',  end=']')
            flop = line and [EmojiCard(c).emojiFlip() for c in line.replace("flop: ", "").split(", ")]
            self.currentHand.flop = flop or []
            
            if self.debugHandAction:
                print(f"#{nil_guard(self.currentHand.id, 0)} - flop: {[c.value for c in (self.currentHand.flop or [])]}")

        elif msg and msg.startswith("turn"):
            line = slice(msg, "[", "]")
            self.currentHand.turn = EmojiCard(line.replace("turn: ", "")).emojiFlip()

            if self.debugHandAction:
                # TODO: format
                print("#\(self.currentHand?.id ?? 0) - turn: \(self.currentHand?.turn?.rawValue ?? '?')")

        elif msg and msg.startswith("river"):
            line = slice(msg, '[', ']')
            self.currentHand.river = EmojiCard(line.replace("river: ", "")).emojiFlip

            if self.debugHandAction:
                # TODO: format
                print("#\(self.currentHand?.id ?? 0) - river: \(self.currentHand?.river?.rawValue ?? '?')")

        else:
            nameIdArray = msg and first(msg.split('" ')).split(" @ ")
            player = first([p for p in self.currentHand.players if p.id == last(nameIdArray)])
            if player:
                if msg and msg.contains("big blind"):
                    bigBlindSize = float(nil_guard(last(msg.split("big blind of ")), 0.0))
                    self.currentHand.big_blind_size = bigBlindSize
                    self.currentHand.big_blind.append(player)

                    if self.debugHandAction:
                        # TODO: format
                        print("#\(self.currentHand?.id ?? 0) - \(player.name ?? 'Unknown Player') posts big \(bigBlindSize)  (Pot: \(self.currentHand?.pot ?? 0))")

                if msg and msg.contains("small blind"):
                    smallBlindSize = float(nil_guard(last(msg.split("small blind of ")), 0.0))
                    self.currentHand.small_blind_size = smallBlindSize
                    if msg.contains("missing"):
                        self.currentHand.missing_small_blinds.append(player)
                    else:
                        self.currentHand.small_blind = player
                    
                    if self.debugHandAction:
                        print("#\(self.currentHand?.id ?? 0) - \(player.name ?? 'Unknown Player') posts small \(smallBlindSize)  (Pot: \(self.currentHand?.pot ?? 0))")
        self.currentHand.lines.append(nil_guard(msg, "unknown line"))
