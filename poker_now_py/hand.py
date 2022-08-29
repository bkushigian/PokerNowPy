'''
hand.py

Created by PJ Gray on 5/27/20.
Adapted to Python by Ben Kushigian on 8/7/2021
Copyright © 2020 Say Goodnight Software. All rights reserved.
'''


from typing import Optional, List, Dict
from datetime import datetime
from card import Card, EmojiCard
from player import Player
from seat import Seat
from util import slice

def nil_guard(opt, other):
    return opt if opt is not None else other

def first(l:List[object]):
    return l[0] if l else None

def last(l:List[object]):
    return l[-1] if l else None

class Hand:
    def __init__(self, name_map=None, num_seats=10):

        self.date: Optional[datetime] = None
        self.hole: Optional[List[Card]] = None
        self.river: Optional[Card] = None
        self.turn: Optional[Card] = None
        self.flop: Optional[List[Card]] = None
        self.second_flop: Optional[List[Card]] = None
        self.second_turn: Optional[Card] = None
        self.second_river: Optional[Card] = None
        self.ran_it_twice: bool = False
        self.pot: float = 0.0
        self.uncalled_bet: float = 0.0
        self.id: int = 0
        self.pn_hand_number = -1
        self.dealer: Optional[Player] = None
        self.missing_small_blinds: List[Player] = []
        self.small_blind: Optional[Player] = None
        self.big_blind: List[Player] = []
        self.players: List[Player] = []
        self.seats: List[Seat] = []
        self.lines: List[str] = []
        self.small_blind_size: float = 0.0
        self.big_blind_size: float = 0.0
        self.printed_showdown: bool = False
        self.name_map = name_map or {}
        self.num_seats = num_seats
    
    
    # requirements as set:
    #   - date
    #   - players
    #   - smallblind  size & id
    #   - bigblinds   size & id
    #   - lines
    #   - dealer
    #   - seats
    #   - hole
    #   - missingSmallBlinds
    #   - flop
    #   - turn
    #   - river
    
    def getPokerStarsDescription(self, hero_name: str, multiplier: float, table_name: str) -> List[str]:
        return '\n'.join(self.pokerStarsDescription(hero_name=hero_name, multiplier=multiplier, table_name=table_name))
    
    def printPokerStarsDescription(self, hero_name: str, multiplier: float, table_name: str):
        lines = self.pokerStarsDescription(hero_name=hero_name, multiplier=multiplier, table_name=table_name)
        print("\n".join(lines))
        
    def pokerStarsDescription(self, hero_name: str, multiplier: float, table_name: str) -> List[str]:
        lines : List[str] = []
        date_string = ""
        date = self.date
        if date:
            date_string = date.strftime("%Y/%m/%d %H:%M:%S")
        
        previous_action: Dict[str:float] = {}
        for player in self.players:
            previous_action[nil_guard(player.id, "error")] = 0.0
        
        sb_id = self.small_blind and self.small_blind.id
        previous_action[nil_guard(sb_id, "error")] = self.small_blind_size * multiplier

        for player in self.big_blind:
            previous_action[nil_guard(player.id, "error")] = float(self.big_blind_size) * multiplier

        found_hole_cards = False
        is_first_action = False
        current_bet = float(self.big_blind_size) * multiplier
        total_pot_size = 0.0
        street_description = "before Flop"
        printed_showdown = False
        printed_second_showdown = False
        for line in self.lines:
            if 'starting hand' in line:
                self.uncalled_bet = 0
                lines.append(f"PokerStars Hand #{self.id}: Hold'em No Limit (${self.small_blind_size * multiplier:.02f}/${self.big_blind_size * multiplier:.02f} USD) - {date_string} ET")
                
                small_blind_seat = 0
                for seat in self.seats:
                    if (self.small_blind and self.small_blind.id) == (seat.player and seat.player.id):
                        small_blind_seat = seat.number
                
                dealer_seat =  small_blind_seat - 1 if small_blind_seat > 1 else 10
                for seat in self.seats:
                    if (self.dealer and self.dealer.id) == (seat.player and seat.player.id):
                        dealer_seat = seat.number
                
                lines.append(f"Table '{table_name}' {self.num_seats}-max Seat #{dealer_seat} is the button")
                        
            if 'Player stacks:' in line:
                playersWithStacks = line.replace("Player stacks: ","").split(" | ")
                for playerWithStack in playersWithStacks:
                    seatNumber = first(playerWithStack.split(" "))
                    playerWithStackNoSeat = playerWithStack.replace(f'{nil_guard(seatNumber, "")} ', "")
                    seatNumber = (seatNumber and seatNumber.replace("#", ""))
                    seatNumberInt = int(nil_guard(seatNumber, "0"))
                    
                    nameIdArray = first(playerWithStackNoSeat.split('" '))
                    nameIdArray = nameIdArray and nameIdArray.replace('"', "").split(" @ ")
                    stackSize = last(playerWithStack.split('" ('))
                    stackSize = stackSize and stackSize.replace(")", "")
                    stackSizeFormatted = f"{float(nil_guard(stackSize, '0.0')) * multiplier:.02f}"
                    name = first(nameIdArray)
                    name = self.name_map.get(name, name) 

                    lines.append(f"Seat {seatNumberInt}: {name} (${stackSizeFormatted} in chips)")
                    
                lines.append(f"{nil_guard((self.small_blind and self.small_blind.name), 'Unknown')}: posts small blind ${self.small_blind_size * multiplier:.02f}")
                
                for big_blind in self.big_blind:
                    lines.append(f"{nil_guard(big_blind.name, 'Unknown')}: posts big blind ${self.big_blind_size * multiplier:.02f}")
            
            if "Your hand" in line:
                lines.append("*** HOLE CARDS ***")
                found_hole_cards = False
                hole_cards = 'error'
                if self.hole:
                    hole_cards = ' '.join([x.emojiFlip().value for x in self.hole])
                    found_hole_cards = True
                lines.append(f"Dealt to {hero_name} [{hole_cards}]")

            if line.startswith('"'):
                if 'bets' in line      or "shows" in line  or\
                   'calls' in line     or "raises" in line or\
                   "checks" in line    or "folds" in line  or\
                   "wins" in line      or "gained" in line or\
                   "collected" in line or "posts a straddle" in line:
                    if not found_hole_cards:
                        lines.append("*** HOLE CARDS ***")
                        found_hole_cards = True
                    nameIdArray = first(line.split('" ')).split(" @ ")
                    player = first([p for p in self.players if p.id == last(nameIdArray)])
                    if player:
                        if 'bets' in line:
                            index = first([i for (i,x) in enumerate(self.seats) if (x.player and x.player.id) == player.id])
                            if index is not None:
                                self.seats[index].preFlopBet = True

                            betSize = float(nil_guard(last(line.replace(" and go all in", "").split(" ")), "0")) * multiplier
                            lines.append(f"{nil_guard(player.name, 'unknown')}: bets {betSize:.02f}")
                            current_bet = betSize
                            is_first_action = False

                            previous_action[nil_guard(player.id, "error")] = betSize

                        if 'posts a straddle' in line:
                            
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                self.seats[index].preFlopBet = True

                            straddleSize = last(line.split("of "))
                            if straddleSize:
                                straddleSize = float(nil_guard(straddleSize, "0.0")) * multiplier
                            else:
                                straddleSize = 0.0
                            lines.append(f"{nil_guard(player.name, 'unknown')}: raises ${straddleSize - current_bet:.02f} to ${straddleSize: .02f}")
                            current_bet = straddleSize
                            previous_action[nil_guard(player.id, "error")] = straddleSize

                        if 'raises' in line:
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                self.seats[index].preFlopBet = True

                            raiseSize = float(last(line.replace(" and go all in", "").split("to ")) or "0.0") * multiplier
                            if is_first_action:
                                lines.append(f"{nil_guard(player.name, 'unknown')}: bets ${raiseSize:.02f}")
                                current_bet = raiseSize
                                is_first_action = False
                            else:
                                lines.append(f"{nil_guard(player.name, 'unknown')}: "
                                             f"raises ${raiseSize - current_bet:.02f} "
                                             f"to ${raiseSize:.02f}")
                                current_bet = raiseSize
                            previous_action[nil_guard(player.id, "error")] = raiseSize

                        if 'calls' in line:
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                self.seats[index].preFlopBet = True

                            call_amount = float(last(line.replace(" and go all in", "").split("calls ")) or "0.0")
                            call_size = call_amount * multiplier
                            if is_first_action:
                                lines.append(f"{nil_guard(player.name, 'unknown')}: bets ${call_size:.02f}")
                                current_bet = call_size
                                is_first_action = False
                            else:
                                uncalled_portion_of_bet = call_size - (previous_action[nil_guard(player.id, "error")] or 0.0)
                                lines.append(f"{nil_guard(player.name, 'unknown')}: calls ${uncalled_portion_of_bet:.02f}")
                            previous_action[nil_guard(player.id, "error")] = call_size

                        if 'checks' in line:
                            lines.append(f"{nil_guard(player.name, 'unknown')}: checks")

                        if 'folds' in line:
                            lines.append(f"{nil_guard(player.name, 'unknown')}: folds")
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                if (street_description == "before Flop") and not self.seats[index].pre_flop_bet:
                                    self.seats[index].summary = f"{nil_guard(player.name, 'Unknown')} folded {street_description} (didn't bet)"
                                else:
                                    self.seats[index].summary = f"{nil_guard(player.name, 'Unknown')} folded {street_description}"
                        
                        if 'shows' in line:
                            hand_components = last(line.split("shows a "))
                            if hand_components is not None:
                                hand_components = hand_components.replace(".", "").split(", ")
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                self.seats[index].showed_hand = hand_components and [EmojiCard(x).emojiFlip().value for x in hand_components]
                                lines.append(f"{player.name or 'unknown'}: "
                                             f"shows [{' '.join([EmojiCard(x).emojiFlip().value for x in (hand_components or [])])}]")
                        
                        if 'collected ' in line:
                            # has showdown
                            if ' from pot with ' in line:
                                win_pot_size = last(line.split(" collected "))
                                if win_pot_size is not None:
                                    win_pot_size = float(nil_guard(first(win_pot_size.split(" from pot with ")), "0.0")) * multiplier

                                # remove missing smalls -- poker stars doesnt do this?
                                win_pot_size = win_pot_size - self.small_blind_size * len(self.missing_small_blinds) * multiplier

                                win_description = last(line.split(" from pot with "))
                                if win_description is not None:
                                    win_description = nil_guard(first(win_description.split(" (")), "error")
                                total_pot_size += win_pot_size
                                if not printed_showdown:
                                    lines.append(f"*** {'FIRST ' if self.ran_it_twice else ''}SHOW DOWN ***")
                                    printed_showdown = True
                                if not printed_second_showdown and "on the second run" in line:
                                        lines.append("*** SECOND SHOW DOWN ***")
                                        printed_second_showdown = True

                                playername = nil_guard(player.name, 'Unknown')
                                amt_won = f"{win_pot_size:.02f}"
                                lines.append(f"{playername} collected ${amt_won} from pot")
                                
                                index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                                assert index is not None
                                if self.seats[index].summary:
                                    self.seats[index].summary += f", and won (${win_pot_size:.02f}) with {win_description}"
                                    pass
                                else:
                                    self.seats[index].summary = f"{nil_guard(player.name, 'Unknown')} showed [] and won (${win_pot_size:.02f}) with {win_description}"

                            else:
                                # no showdown
                                win_pot_size = last(line.split(" collected "))
                                if win_pot_size is not None:
                                    win_pot_size = float(nil_guard(first(win_pot_size.split(" from pot")), "0.0")) * multiplier
                                else:
                                    win_pot_size = 0.0

                                # remove missing smalls -- poker stars doesnt do this?
                                win_pot_size = win_pot_size - self.small_blind_size * len(self.missing_small_blinds) * multiplier

                                
                                if self.flop is None:
                                    preFlopAction = 0.0
                                    
                                    for p in self.players:
                                        preFlopAction = preFlopAction + (nil_guard(previous_action[nil_guard(p.id, "error")], 0.0))
                                    
                                    # catching edge case of folding around preflop
                                    if preFlopAction == float(self.big_blind_size + self.small_blind_size) * multiplier:
                                        win_pot_size = float(self.small_blind_size) * multiplier
                                        lines.append(f"Uncalled bet (${self.big_blind_size * multiplier:.02f}) returned to {nil_guard(player.name, 'Unknown')}")
                                    else:
                                        if self.uncalled_bet > 0:
                                            lines.append(f"Uncalled bet (${self.uncalled_bet * multiplier:.02f}) returned to {nil_guard(player.name, 'Unknown')}")
                                else:
                                    if self.uncalled_bet > 0:
                                        lines.append(f"Uncalled bet (${self.uncalled_bet * multiplier:.02f}) returned to {nil_guard(player.name, 'Unknown')}")

                                total_pot_size += win_pot_size
                                playername = nil_guard(player.name, 'Unknown')
                                amt_won = f"{win_pot_size:.02f}"
                                lines.append(f"{playername} collected ${amt_won} from pot")
                                index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                                if index is not None:
                                    self.seats[index].summary = f"{nil_guard(player.name, 'Unknown')} collected (${win_pot_size:.02f})"
                            
            
            if line.startswith("Uncalled bet"):
                uncalled_string = first(line.split(" returned to"))
                if uncalled_string is not None:
                    uncalled_string = uncalled_string.replace("Uncalled bet of ", "")
                try:
                    self.uncalled_bet = float(nil_guard(uncalled_string, "0.0"))
                except:
                    self.uncalled_bet = 0.0
            
            if line.lower().startswith("all players in hand choose to run it twice."):
                self.ran_it_twice = True

            if line.lower().startswith("flop:"):
                self.flop = [EmojiCard(c) for c in slice(line, '[', ']').split(', ')]
                lines.append(f"*** {'FIRST ' if self.ran_it_twice else ''}FLOP *** [{nil_guard(' '.join([x.emojiFlip().value for x in (self.flop or [])]), 'error')}]")
                is_first_action = True
                current_bet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0.0
                street_description = "on the Flop"

            if line.lower().startswith("flop (second run):"):
                self.second_flop = [EmojiCard(c) for c in slice(line, '[', ']').split(', ')]
                lines.append(f"*** SECOND FLOP *** [{nil_guard(' '.join([x.emojiFlip().value for x in (self.second_flop or [])]), 'error')}]")
                is_first_action = True
                current_bet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0.0
                street_description = "on the Flop"

            if line.lower().startswith("turn:"):
                try:
                    self.turn = EmojiCard(slice(line, '[', ']'))
                except:
                    self.turn = EmojiCard.error
                lines.append(f"*** {'FIRST ' if self.ran_it_twice else ''}TURN *** [{nil_guard(' '.join(x.emojiFlip().value for x in (self.flop or [])), 'error')}] "
                             f"[{nil_guard(self.turn and self.turn.emojiFlip().value, 'error')}]")
                is_first_action = True
                current_bet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0
                street_description = "on the Turn"

            if line.lower().startswith("turn (second run):"):
                try:
                    self.second_turn = EmojiCard(slice(line, '[', ']'))
                except:
                    self.second_turn = EmojiCard.error
                # Get the most recent flop
                flop = self.second_flop or self.flop
                lines.append(f"*** SECOND TURN *** [{' '.join(x.emojiFlip().value for x in flop)}] "
                             f"[{nil_guard(self.second_turn and self.second_turn.emojiFlip().value, 'error')}]")
                is_first_action = True
                current_bet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0
                street_description = "on the Turn"

            if line.lower().startswith("river:"):
                try:
                    self.river = EmojiCard(slice(line, '[', ']'))
                except:
                    self.river = EmojiCard.error
                lines.append(f"*** {'FIRST ' if self.ran_it_twice else ''}RIVER *** [{nil_guard(' '.join(x.emojiFlip().value for x in self.flop), 'error')} "
                             f"{nil_guard(self.turn and self.turn.emojiFlip().value, 'error')}] "
                             f"[{nil_guard(self.river and self.river.emojiFlip().value, 'error')}]")
                is_first_action = True
                current_bet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0.0

                street_description = "on the River"
            
            if line.lower().startswith("river (second run):"):
                try:
                    self.second_river = EmojiCard(slice(line, '[', ']'))
                except:
                    self.second_river = EmojiCard.error
                # Get the most recent flop and turn
                flop = self.second_flop or self.flop
                turn = self.second_turn or self.turn
                lines.append(f"*** SECOND RIVER *** [{' '.join(x.emojiFlip().value for x in flop)} "
                             f"{nil_guard(turn and turn.emojiFlip().value, 'error')}] "
                             f"[{nil_guard(self.second_river and self.second_river.emojiFlip().value, 'error')}]")
                is_first_action = True
                current_bet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0.0

                street_description = "on the River"

            if last(self.lines) == line:
                lines.append("*** SUMMARY ***")
                lines.append(f"Total pot: ${total_pot_size:.02f} | Rake $0.00")
                if self.ran_it_twice:
                    lines.append("Hand was run twice")
                board: List[Card] = []
                board += nil_guard(self.flop, [])
                if self.turn: board.append(self.turn)
                if self.river: board.append(self.river)
                
                if len(board) > 0:
                    lines.append(f"{'FIRST ' if self.ran_it_twice else ''}Board: [{' '.join([x.emojiFlip().value for x in board])}]")
                
                if self.ran_it_twice:
                    board = []
                    board += self.second_flop or self.flop
                    board.append(self.second_turn or self.turn)
                    board.append(self.second_river or self.river)
                    lines.append(f"SECOND Board: [{' '.join([x.emojiFlip().value for x in board])}]")


                for seat in self.seats:
                    summary = seat.summary
                    if self.dealer and seat.player and self.dealer.id == seat.player.id:
                        # TODO: Not sure what this line does
                        summary = summary.replace(nil_guard(seat.player.name, "Unknown"), f"{nil_guard(seat.player.name, 'Unknown')} (button)")

                    if self.small_blind and seat.player and self.small_blind.id == seat.player.id:
                        summary = summary.replace(nil_guard(seat.player.name, "Unknown"), f"{nil_guard(seat.player.name, 'Unknown')} (small blind)")

                    for big_blind in self.big_blind:
                        if big_blind and seat.player and big_blind.id == seat.player.id:
                            summary = summary.replace(nil_guard(seat.player.name, "Unknown"), f"{nil_guard(seat.player.name, 'Unknown')} (big blind)")
                    
                    if seat.showed_hand is not None and '[]' not in summary:
                        lines.append(f"Seat {seat.number}: {summary} [{nil_guard(' '.join(seat.showed_hand), 'error')}]")
                    else:
                        try:
                            summary = summary.replace("[]", f"[{nil_guard(' '.join(seat.showed_hand), 'error')}]")
                        except:
                            pass
                        lines.append(f"Seat {seat.number}: {summary}")
                lines.append("")

        return lines

    def getSwCDescription(self, hero_name: str, multiplier: float, table_name: str) -> List[str]:
        return '\n'.join(self.swcDescription(hero_name=hero_name, multiplier=multiplier, table_name=table_name))
    
    def printSwCDescription(self, hero_name: str, multiplier: float, table_name: str):
        lines = self.swcDescription(hero_name=hero_name, multiplier=multiplier, table_name=table_name)
        print("\n".join(lines))
        
    def swcDescription(self, hero_name: str, multiplier: float, table_name: str) -> List[str]:
        lines : List[str] = []
        date_string = ""
        date = self.date
        if date:
            date_string = date.strftime("%Y/%m/%d %H:%M:%S")
        
        previous_action: Dict[str:float] = {}
        for player in self.players:
            previous_action[nil_guard(player.id, "error")] = 0.0
        
        sb_id = self.small_blind and self.small_blind.id
        previous_action[nil_guard(sb_id, "error")] = self.small_blind_size * multiplier

        for player in self.big_blind:
            previous_action[nil_guard(player.id, "error")] = float(self.big_blind_size) * multiplier

        found_hole_cards = False
        is_first_action = False
        current_bet = float(self.big_blind_size) * multiplier
        total_pot_size = 0.0
        street_description = "before Flop"
        printed_showdown = False
        printed_second_showdown = False
        for line in self.lines:
            if 'starting hand' in line:
                self.uncalled_bet = 0
                lines.append(f"SwCPoker Hand #{self.id}: Hold'em No Limit ({self.small_blind_size * multiplier:.02f}/{self.big_blind_size * multiplier:.02f} USD) - {date_string} ET")
                
                small_blind_seat = 0
                for seat in self.seats:
                    if (self.small_blind and self.small_blind.id) == (seat.player and seat.player.id):
                        small_blind_seat = seat.number
                
                dealer_seat =  small_blind_seat - 1 if small_blind_seat > 1 else 10
                for seat in self.seats:
                    if (self.dealer and self.dealer.id) == (seat.player and seat.player.id):
                        dealer_seat = seat.number
                
                lines.append(f"Table '{table_name}' {self.num_seats}-max (Real Money) Seat #{dealer_seat} is the button")
                        
            if 'Player stacks:' in line:
                playersWithStacks = line.replace("Player stacks: ","").split(" | ")
                for playerWithStack in playersWithStacks:
                    seatNumber = first(playerWithStack.split(" "))
                    playerWithStackNoSeat = playerWithStack.replace(f'{nil_guard(seatNumber, "")} ', "")
                    seatNumber = (seatNumber and seatNumber.replace("#", ""))
                    seatNumberInt = int(nil_guard(seatNumber, "0"))
                    
                    nameIdArray = first(playerWithStackNoSeat.split('" '))
                    nameIdArray = nameIdArray and nameIdArray.replace('"', "").split(" @ ")
                    stackSize = last(playerWithStack.split('" ('))
                    stackSize = stackSize and stackSize.replace(")", "")
                    stackSizeFormatted = f"{float(nil_guard(stackSize, '0.0')) * multiplier:.02f}"
                    name = first(nameIdArray)
                    name = self.name_map.get(name, name) 

                    lines.append(f"Seat {seatNumberInt}: {name} ({stackSizeFormatted} in chips)")
                    
                lines.append(f"{nil_guard((self.small_blind and self.small_blind.name), 'Unknown')}: posts small blind {self.small_blind_size * multiplier:.02f}")
                
                for big_blind in self.big_blind:
                    lines.append(f"{nil_guard(big_blind.name, 'Unknown')}: posts big blind {self.big_blind_size * multiplier:.02f}")
            
            if "Your hand" in line:
                lines.append("*** HOLE CARDS ***")
                found_hole_cards = False
                hole_cards = 'error'
                if self.hole:
                    hole_cards = ' '.join([x.emojiFlip().value for x in self.hole])
                    found_hole_cards = True
                lines.append(f"Dealt to {hero_name} [{hole_cards}]")

            if line.startswith('"'):
                if 'bets' in line      or "shows" in line  or\
                   'calls' in line     or "raises" in line or\
                   "checks" in line    or "folds" in line  or\
                   "wins" in line      or "gained" in line or\
                   "collected" in line or "posts a straddle" in line:
                    if not found_hole_cards:
                        lines.append("*** HOLE CARDS ***")
                        found_hole_cards = True
                    nameIdArray = first(line.split('" ')).split(" @ ")
                    player = first([p for p in self.players if p.id == last(nameIdArray)])
                    if player:
                        if 'bets' in line:
                            index = first([i for (i,x) in enumerate(self.seats) if (x.player and x.player.id) == player.id])
                            if index is not None:
                                self.seats[index].preFlopBet = True

                            betSize = float(nil_guard(last(line.replace(" and go all in", "").split(" ")), "0")) * multiplier
                            lines.append(f"{nil_guard(player.name, 'unknown')}: bets {betSize:.02f}")
                            current_bet = betSize
                            is_first_action = False

                            previous_action[nil_guard(player.id, "error")] = betSize

                        if 'posts a straddle' in line:
                            
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                self.seats[index].preFlopBet = True

                            straddleSize = last(line.split("of "))
                            if straddleSize:
                                straddleSize = float(nil_guard(straddleSize, "0.0")) * multiplier
                            else:
                                straddleSize = 0.0
                            lines.append(f"{nil_guard(player.name, 'unknown')}: raises {straddleSize - current_bet:.02f} to {straddleSize: .02f}")
                            current_bet = straddleSize
                            previous_action[nil_guard(player.id, "error")] = straddleSize

                        if 'raises' in line:
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                self.seats[index].preFlopBet = True

                            raiseSize = float(last(line.replace(" and go all in", "").split("to ")) or "0.0") * multiplier
                            if is_first_action:
                                lines.append(f"{nil_guard(player.name, 'unknown')}: bets {raiseSize:.02f}")
                                current_bet = raiseSize
                                is_first_action = False
                            else:
                                lines.append(f"{nil_guard(player.name, 'unknown')}: "
                                             f"raises {raiseSize - current_bet:.02f} "
                                             f"to {raiseSize:.02f}")
                                current_bet = raiseSize
                            previous_action[nil_guard(player.id, "error")] = raiseSize

                        if 'calls' in line:
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                self.seats[index].preFlopBet = True

                            call_amount = float(last(line.replace(" and go all in", "").split("calls ")) or "0.0")
                            call_size = call_amount * multiplier
                            if is_first_action:
                                lines.append(f"{nil_guard(player.name, 'unknown')}: bets {call_size:.02f}")
                                current_bet = call_size
                                is_first_action = False
                            else:
                                uncalled_portion_of_bet = call_size - (previous_action[nil_guard(player.id, "error")] or 0.0)
                                lines.append(f"{nil_guard(player.name, 'unknown')}: calls {uncalled_portion_of_bet:.02f}")
                            previous_action[nil_guard(player.id, "error")] = call_size

                        if 'checks' in line:
                            lines.append(f"{nil_guard(player.name, 'unknown')}: checks")

                        if 'folds' in line:
                            lines.append(f"{nil_guard(player.name, 'unknown')}: folds")
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                if (street_description == "before Flop") and not self.seats[index].pre_flop_bet:
                                    self.seats[index].summary = f"{nil_guard(player.name, 'Unknown')} folded {street_description} (didn't bet)"
                                else:
                                    self.seats[index].summary = f"{nil_guard(player.name, 'Unknown')} folded {street_description}"
                        
                        if 'shows' in line:
                            hand_components = last(line.split("shows a "))
                            if hand_components is not None:
                                hand_components = hand_components.replace(".", "").split(", ")
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                self.seats[index].showed_hand = hand_components and [EmojiCard(x).emojiFlip().value for x in hand_components]
                                lines.append(f"{player.name or 'unknown'}: "
                                             f"shows [{' '.join([EmojiCard(x).emojiFlip().value for x in (hand_components or [])])}]")
                        
                        if 'collected ' in line:
                            # has showdown
                            if ' from pot with ' in line:
                                win_pot_size = last(line.split(" collected "))
                                if win_pot_size is not None:
                                    win_pot_size = float(nil_guard(first(win_pot_size.split(" from pot with ")), "0.0")) * multiplier

                                # remove missing smalls -- poker stars doesnt do this?
                                win_pot_size = win_pot_size - self.small_blind_size * len(self.missing_small_blinds) * multiplier

                                win_description = last(line.split(" from pot with "))
                                if win_description is not None:
                                    win_description = nil_guard(first(win_description.split(" (")), "error")
                                total_pot_size += win_pot_size
                                if not printed_showdown:
                                    lines.append(f"*** {'FIRST ' if self.ran_it_twice else ''}SHOW DOWN ***")
                                    printed_showdown = True
                                if not printed_second_showdown and "on the second run" in line:
                                        lines.append("*** SECOND SHOW DOWN ***")
                                        printed_second_showdown = True

                                playername = nil_guard(player.name, 'Unknown')
                                amt_won = f"{win_pot_size:.02f}"
                                lines.append(f"{playername} collected {amt_won} from pot")
                                
                                index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                                assert index is not None
                                if self.seats[index].summary:
                                    self.seats[index].summary += f", and won ({win_pot_size:.02f}) with {win_description}"
                                    pass
                                else:
                                    self.seats[index].summary = f"{nil_guard(player.name, 'Unknown')} showed [] and won ({win_pot_size:.02f}) with {win_description}"

                            else:
                                # no showdown
                                win_pot_size = last(line.split(" collected "))
                                if win_pot_size is not None:
                                    win_pot_size = float(nil_guard(first(win_pot_size.split(" from pot")), "0.0")) * multiplier
                                else:
                                    win_pot_size = 0.0

                                # remove missing smalls -- poker stars doesnt do this?
                                win_pot_size = win_pot_size - self.small_blind_size * len(self.missing_small_blinds) * multiplier

                                
                                if self.flop is None:
                                    preFlopAction = 0.0
                                    
                                    for p in self.players:
                                        preFlopAction = preFlopAction + (nil_guard(previous_action[nil_guard(p.id, "error")], 0.0))
                                    
                                    # catching edge case of folding around preflop
                                    if preFlopAction == float(self.big_blind_size + self.small_blind_size) * multiplier:
                                        win_pot_size = float(self.small_blind_size) * multiplier
                                        lines.append(f"Uncalled bet ({self.big_blind_size * multiplier:.02f}) returned to {nil_guard(player.name, 'Unknown')}")
                                    else:
                                        if self.uncalled_bet > 0:
                                            lines.append(f"Uncalled bet ({self.uncalled_bet * multiplier:.02f}) returned to {nil_guard(player.name, 'Unknown')}")
                                else:
                                    if self.uncalled_bet > 0:
                                        lines.append(f"Uncalled bet ({self.uncalled_bet * multiplier:.02f}) returned to {nil_guard(player.name, 'Unknown')}")

                                total_pot_size += win_pot_size
                                playername = nil_guard(player.name, 'Unknown')
                                amt_won = f"{win_pot_size:.02f}"
                                lines.append(f"{playername} collected {amt_won} from pot")
                                index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                                if index is not None:
                                    self.seats[index].summary = f"{nil_guard(player.name, 'Unknown')} collected ({win_pot_size:.02f})"
                            
            
            if line.startswith("Uncalled bet"):
                uncalled_string = first(line.split(" returned to"))
                if uncalled_string is not None:
                    uncalled_string = uncalled_string.replace("Uncalled bet of ", "")
                try:
                    self.uncalled_bet = float(nil_guard(uncalled_string, "0.0"))
                except:
                    self.uncalled_bet = 0.0
            
            if line.lower().startswith("all players in hand choose to run it twice."):
                self.ran_it_twice = True

            if line.lower().startswith("flop:"):
                self.flop = [EmojiCard(c) for c in slice(line, '[', ']').split(', ')]
                lines.append(f"*** {'FIRST ' if self.ran_it_twice else ''}FLOP *** [{nil_guard(' '.join([x.emojiFlip().value for x in (self.flop or [])]), 'error')}]")
                is_first_action = True
                current_bet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0.0
                street_description = "on the Flop"

            if line.lower().startswith("flop (second run):"):
                self.second_flop = [EmojiCard(c) for c in slice(line, '[', ']').split(', ')]
                lines.append(f"*** SECOND FLOP *** [{nil_guard(' '.join([x.emojiFlip().value for x in (self.second_flop or [])]), 'error')}]")
                is_first_action = True
                current_bet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0.0
                street_description = "on the Flop"

            if line.lower().startswith("turn:"):
                try:
                    self.turn = EmojiCard(slice(line, '[', ']'))
                except:
                    self.turn = EmojiCard.error
                lines.append(f"*** {'FIRST ' if self.ran_it_twice else ''}TURN *** [{nil_guard(' '.join(x.emojiFlip().value for x in (self.flop or [])), 'error')}] "
                             f"[{nil_guard(self.turn and self.turn.emojiFlip().value, 'error')}]")
                is_first_action = True
                current_bet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0
                street_description = "on the Turn"

            if line.lower().startswith("turn (second run):"):
                try:
                    self.second_turn = EmojiCard(slice(line, '[', ']'))
                except:
                    self.second_turn = EmojiCard.error
                # Get the most recent flop
                flop = self.second_flop or self.flop
                lines.append(f"*** SECOND TURN *** [{' '.join(x.emojiFlip().value for x in flop)}] "
                             f"[{nil_guard(self.second_turn and self.second_turn.emojiFlip().value, 'error')}]")
                is_first_action = True
                current_bet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0
                street_description = "on the Turn"

            if line.lower().startswith("river:"):
                try:
                    self.river = EmojiCard(slice(line, '[', ']'))
                except:
                    self.river = EmojiCard.error
                lines.append(f"*** {'FIRST ' if self.ran_it_twice else ''}RIVER *** [{nil_guard(' '.join(x.emojiFlip().value for x in self.flop), 'error')} "
                             f"{nil_guard(self.turn and self.turn.emojiFlip().value, 'error')}] "
                             f"[{nil_guard(self.river and self.river.emojiFlip().value, 'error')}]")
                is_first_action = True
                current_bet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0.0

                street_description = "on the River"
            
            if line.lower().startswith("river (second run):"):
                try:
                    self.second_river = EmojiCard(slice(line, '[', ']'))
                except:
                    self.second_river = EmojiCard.error
                # Get the most recent flop and turn
                flop = self.second_flop or self.flop
                turn = self.second_turn or self.turn
                lines.append(f"*** SECOND RIVER *** [{' '.join(x.emojiFlip().value for x in flop)} "
                             f"{nil_guard(turn and turn.emojiFlip().value, 'error')}] "
                             f"[{nil_guard(self.second_river and self.second_river.emojiFlip().value, 'error')}]")
                is_first_action = True
                current_bet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0.0

                street_description = "on the River"

            if last(self.lines) == line:
                lines.append("*** SUMMARY ***")
                lines.append(f"Total pot: {total_pot_size:.02f} | Rake 0")
                if self.ran_it_twice:
                    lines.append("Hand was run twice")
                board: List[Card] = []
                board += nil_guard(self.flop, [])
                if self.turn: board.append(self.turn)
                if self.river: board.append(self.river)
                
                if len(board) > 0:
                    lines.append(f"{'FIRST ' if self.ran_it_twice else ''}Board: [{' '.join([x.emojiFlip().value for x in board])}]")
                
                if self.ran_it_twice:
                    board = []
                    board += self.second_flop or self.flop
                    board.append(self.second_turn or self.turn)
                    board.append(self.second_river or self.river)
                    lines.append(f"SECOND Board: [{' '.join([x.emojiFlip().value for x in board])}]")


                for seat in self.seats:
                    summary = seat.summary
                    if self.dealer and seat.player and self.dealer.id == seat.player.id:
                        # TODO: Not sure what this line does
                        summary = summary.replace(nil_guard(seat.player.name, "Unknown"), f"{nil_guard(seat.player.name, 'Unknown')} (button)")

                    if self.small_blind and seat.player and self.small_blind.id == seat.player.id:
                        summary = summary.replace(nil_guard(seat.player.name, "Unknown"), f"{nil_guard(seat.player.name, 'Unknown')} (small blind)")

                    for big_blind in self.big_blind:
                        if big_blind and seat.player and big_blind.id == seat.player.id:
                            summary = summary.replace(nil_guard(seat.player.name, "Unknown"), f"{nil_guard(seat.player.name, 'Unknown')} (big blind)")
                    
                    if seat.showed_hand is not None and '[]' not in summary:
                        lines.append(f"Seat {seat.number}: {summary} [{nil_guard(' '.join(seat.showed_hand), 'error')}]")
                    else:
                        try:
                            summary = summary.replace("[]", f"[{nil_guard(' '.join(seat.showed_hand), 'error')}]")
                        except:
                            pass
                        lines.append(f"Seat {seat.number}: {summary}")
                lines.append("")

        return lines