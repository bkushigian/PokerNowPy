'''
game.py

Created by PJ Gray on 5/27/20.
Adapted to Python by Ben Kushigian on 8/7/2021
Copyright © 2020 Say Goodnight Software. All rights reserved.
'''

from typing import List, Optional, Dict
from util import nil_guard, first, last, hash_str_as_id
from datetime import datetime, timezone

from player import Player
from hand import Hand
from card import EmojiCard
from seat import Seat

class Game:

    def __init__(self, rows: List[Dict[str, str]],
                       debug_hand_action=False,
                       name_map: Dict[str,str]=None,
                       num_seats=10,
                       chip_formatter=None):
    
        self.debug_hand_action: bool = debug_hand_action
        self.show_errors: bool = True
        self.hands: List[Hand] = []
        self.current_hand: Optional[Hand] = None
        self.name_map = name_map or {}
        self.chip_formatter = chip_formatter or (lambda amt: f"${amt:0.2f}")

        self.dealer_id: Optional[str] = None
        self.num_seats = num_seats
        self.init(rows)

    def init(self, rows: List[Dict[str,str]]):
        # super.init()

        last_row = last(rows)
        at = last_row["at"] if last_row else None
        if self.isSupportedLog(at=at):
            for row in rows[::-1]:
                self.parse_line(msg=row["entry"], at=row["at"], order=row["order"])
        else:
            print("Unsupported log format: the PokerNow.club file format has changed since this log was generated")
        
    def isSupportedLog(self, at: str) -> bool:
        format_str = "%Y-%m-%dT%H:%M:%S.%f%z"   # from Swift format string "yyyy-MM-dd'T'HH:mm:ss.SSSZ"

        try:
            date = datetime.strptime(nil_guard(at, ""), format_str)
        except Exception as e:
            print(e)
            raise RuntimeError("Cannot parse log's date")
            
        oldestSupportedLog = datetime.fromtimestamp(1594731595, tz=timezone.utc)
        
        return date > oldestSupportedLog
    
    def parse_line(self, msg: Optional[str], at: Optional[str], order: Optional[str]):
        format_str = "%Y-%m-%dT%H:%M:%S.%f%z"   # from Swift format string "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
        date = datetime.strptime(at, format_str) if at else datetime.strptime("")
        hand_number = -1
        
        if msg and msg.startswith("-- starting hand "):
            # -- starting hand #1  (No Limit Texas Hold'em) (dealer: ""Superman @ lcLCU4HVrS"") --
            #
            # This contains hand number, game type, and current dealer
            starting_hand_components = msg.split(' (dealer: "')
            hand_number = starting_hand_components[0].split("#")[1].split()[0]
            unparsed_dealer = last(starting_hand_components).replace('") --', "")
            
            # for legacy logs
            dealer_separator = " @ "
            if unparsed_dealer and " # " in unparsed_dealer:
                dealer_separator = " # "

            hand = Hand(name_map=self.name_map, num_seats=self.num_seats, chip_formatter=self.chip_formatter)
            if "dead button" in msg:
                hand.id = hash_str_as_id(f"deadbutton-{date.timestamp() if date else 0}")
                hand.dealer = None
            else:
                dealer_name_ids = unparsed_dealer and unparsed_dealer.split(dealer_separator)
                self.dealer_id = dealer_name_ids and last(dealer_name_ids)
                hand.id = hash_str_as_id(f"{nil_guard(self.dealer_id, 'error')}-{date.timestamp() if date else 0}")
                
            hand.pn_hand_number = hand_number
            hand.date = date
            self.current_hand = hand
            self.hands.append(hand)
        elif msg and msg.startswith("-- ending hand "):
            if self.debug_hand_action:
                print("----")
        elif msg and msg.startswith("Player stacks"):
            # Player stacks: #1 ""Superman @ lcLCU4HVrS"" (10000) | #2 ""LexLuthor @ 7ZOX07XXIG"" (28991)
            # 
            # 1. Players in this hand
            # 2. Each player's stack size
            # 3. Each player's seat number

            players_with_stacks = msg.replace("Player stacks: ", "").split(" | ")
            players : List[Player] = []
            
            for player_with_stack in players_with_stacks:
                seat_number = first(player_with_stack.split(" "))
                if not seat_number:
                    raise RuntimeError(f"Illegal seat_number {seat_number} in hand #{hand_number}")
                if seat_number:
                    player_with_stack_no_seat = player_with_stack.replace(f"{seat_number} ", "")
                seat_number_int = int(seat_number.replace("#", "") if seat_number is not None else "0")
                
                name_ids = first(player_with_stack_no_seat.split('\" '))
                name_ids = name_ids and name_ids.replace('"', "").split(" @ ")
                name = name_ids[0]
                name = self.name_map.get(name, name)
                if name is None:
                    raise RuntimeError(f"Illegal State: expected player name but found None: hand #{hand_number}")
                pid = name_ids[1]
                stack_size = player_with_stack.split('" (')[-1].replace(")", "")
                if not stack_size:
                    stack_size = "0"
                
                player = Player(admin=False, id=pid, stack=float(stack_size), name=name)
                players.append(player)
                
                if not self.current_hand:
                    raise RuntimeError(f"Game doesn't have a current_hand (hand #{hand_number})")
                self.current_hand.seats.append(Seat(player=player, summary=f"{player.name} didn't show and lost", pre_flop_bet=False, number=seat_number_int))
                        
            self.current_hand.players = players
            dealer = first([x for x in players if x.id == self.dealer_id])
            if dealer:
                self.current_hand.dealer = dealer
        elif msg and msg.startswith("Your hand is "):
            # Your hand is Q♠, Q♥
            #
            # This line gives the hero's hand
            self.current_hand.hole = [EmojiCard(c.strip()) for c in  msg.replace("Your hand is ", "").split(", ")]

            if self.debug_hand_action:
                print(f"#{nil_guard(self.current_hand.id, 0)} - hole cards: {[c.value for c in nil_guard(self.current_hand.hole, [])]}")
        elif msg and msg.startswith("flop"):
            line = slice(msg, start='[',  end=']')
            flop = line and [EmojiCard(c).emojiFlip() for c in line.replace("flop: ", "").split(", ")]
            self.current_hand.flop = flop or []
            
            if self.debug_hand_action:
                print(f"#{nil_guard(self.current_hand.id, 0)} - flop: {[c.value for c in (self.current_hand.flop or [])]}")

        elif msg and msg.startswith("turn"):
            line = slice(msg, "[", "]")
            self.current_hand.turn = EmojiCard(line.replace("turn: ", "")).emojiFlip()

            if self.debug_hand_action:
                # TODO: format
                print(f"#{nil_guard(self.current_hand and self.current_hand.id,  0)} - turn: {nil_guard(self.current_hand and self.current_hand.turn.value, '?')}")

        elif msg and msg.startswith("river"):
            line = slice(msg, '[', ']')
            self.current_hand.river = EmojiCard(line.replace("river: ", "")).emojiFlip

            if self.debug_hand_action:
                # TODO: format
                print("#\(self.currentHand?.id ?? 0) - river: \(self.currentHand?.river?.rawValue ?? '?')")

        else:
            name_ids = msg and first(msg.split('" ')).split(" @ ")
            player = first([p for p in self.current_hand.players if p.id == last(name_ids)]) if self.current_hand else None
            if player:
                if msg and "big blind" in msg:
                    bigBlindSize = float(nil_guard(last(msg.split("big blind of ")), 0.0))
                    self.current_hand.big_blind_size = bigBlindSize
                    self.current_hand.big_blind.append(player)

                    if self.debug_hand_action:
                        # TODO: format
                        print("#\(self.currentHand?.id ?? 0) - \(player.name ?? 'Unknown Player') posts big \(bigBlindSize)  (Pot: \(self.currentHand?.pot ?? 0))")

                if msg and "small blind" in msg:
                    if "and go all in" in msg:
                        msg = msg.split('and go all in')[0]
                    small_blind_size = float(nil_guard(msg.split("small blind of ")[-1], 0.0))
                    self.current_hand.small_blind_size = small_blind_size
                    if "missing" in msg:
                        self.current_hand.missing_small_blinds.append(player)
                    else:
                        self.current_hand.small_blind = player
                    
                    if self.debug_hand_action:
                        print("#\(self.currentHand?.id ?? 0) - \(player.name ?? 'Unknown Player') posts small \(smallBlindSize)  (Pot: \(self.currentHand?.pot ?? 0))")
        if self.current_hand:
            self.current_hand.lines.append(nil_guard(msg, "unknown line"))
