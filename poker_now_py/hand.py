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

def nil_guard(opt, other):
    return opt if opt is not None else other

def first(l:List[object]):
    return l[0] if l else None

def last(l:List[object]):
    return l[-1] if l else None

class Hand:
    def __init__(self, date:Optional[datetime]=None,
                       hole:Optional[List[Card]]=None,
                       river:Optional[Card]=None,
                       turn:Optional[Card]=None,
                       flop:Optional[List[Card]]=None,
                       pot:float=0.0,
                       uncalled_bet:float=0.0,
                       id:int=0,
                       dealer:Optional[Player]=None,
                       missing_small_blinds:Optional[List[Player]]=None,
                       small_blind:Optional[Player]=None,
                       big_blind:Optional[List[Player]]=None,
                       players:Optional[List[Player]]=None,
                       seats:Optional[List[Seat]]=None,
                       lines:Optional[List[str]]=None,
                       small_blind_size:float=0.0,
                       big_blind_size:float=0.0,
                       printed_showdown:bool=False):

        self.date: Optional[datetime] = date
        self.hole: Optional[List[Card]] = hole
        self.river: Optional[Card] = river
        self.turn: Optional[Card] = turn
        self.flop: Optional[List[Card]] = flop
        self.pot: float = pot
        self.uncalled_bet: float = uncalled_bet
        self.id: int = id
        self.dealer: Optional[Player] = dealer
        self.missing_small_blinds: List[Player] = missing_small_blinds or []
        self.small_blind: Optional[Player] = small_blind
        self.big_blind: List[Player] = big_blind or []
        self.players: List[Player] = players or []
        self.seats: List[Seat] = seats or []
        self.lines: List[str] = lines or []
        self.small_blind_size: float = small_blind_size
        self.big_blind_size: float = big_blind_size
        self.printed_showdown: bool = printed_showdown
    
    
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
        return self.pokerStarsDescription(hero_name=hero_name, multiplier=multiplier, table_name=table_name)
    
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
        for line in self.lines:
            if line.contains("starting hand"):
                self.uncalled_bet = 0
                lines.append(f"PokerStars Hand #{self.id}: Hold'em No Limit ({self.small_blind_size * multiplier:.02f}/{self.big_blind_size * multiplier:.02f} USD) - {date_string} ET")
                
                small_blind_seat = 0
                for seat in self.seats:
                    if (self.small_blind and self.small_blind.id) == (seat.player and seat.player.id):
                        small_blind_seat = seat.number
                
                dealer_seat =  small_blind_seat - 1 if small_blind_seat > 1 else 10
                for seat in self.seats:
                    if (self.dealer and self.dealer.id) == (seat.player and seat.player.id):
                        dealer_seat = seat.number
                
                lines.append(f"Table '{table_name}' 10-max Seat #{dealer_seat} is the button")
                        
            if line.contains("Player stacks:"):
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

                    lines.append(f"Seat {seatNumberInt}: {nil_guard(nameIdArray and first(nameIdArray), 'error')} ({stackSizeFormatted} in chips)")
                    
                lines.append(f"{nil_guard((self.smallBlind and self.smallBlind.name), 'Unknown')}: posts small blind {self.smallBlindSize * multiplier:.02f}")
                
                for bigBlind in self.bigBlind:
                    lines.append(f"{nil_guard(bigBlind.name, 'Unknown')}: posts big blind {self.bigBlindSize * multiplier:.02f}")
            
            if line.contains("Your hand"):
                lines.append("*** HOLE CARDS ***")
                found_hole_cards = False
                hole_cards = 'error'
                if self.hole:
                    hole_cards = ' '.join([x.value for x in self.hole])
                    found_hole_cards = True
                lines.append(f"Dealt to {hero_name} [{hole_cards}]")

            if line.startswith('"'):
                if line.contains("bets")      or line.contains("shows")  or\
                   line.contains("calls")     or line.contains("raises") or\
                   line.contains("checks")    or line.contains("folds")  or\
                   line.contains("wins")      or line.contains("gained") or\
                   line.contains("collected") or line.contains("posts a straddle"):
                    if not found_hole_cards:
                        lines.append("*** HOLE CARDS ***")
                        found_hole_cards = True
                    nameIdArray = first(line.split('" ')).split(" @ ")
                    player = first([p for p in self.players if p.id == last(nameIdArray)])
                    if player:
                        if line.contains("bets"):
                            index = first([i for (i,x) in enumerate(self.seats) if (x.player and x.player.id) == player.id])
                            if index is not None:
                                self.seats[index].preFlopBet = True

                            betSize = float(nil_guard(last(line.replace(" and go all in", "").split(" ")), "0")) * multiplier
                            lines.append(f"{nil_guard(player.name, 'unknown')}: bets {betSize:.02f}")
                            currentBet = betSize
                            isFirstAction = False

                            previous_action[nil_guard(player.id, "error")] = betSize

                        if line.contains("posts a straddle"):
                            
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                self.seats[index].preFlopBet = True

                            straddleSize = last(line.split("of "))
                            if straddleSize:
                                straddleSize = float(nil_guard(straddleSize, "0.0")) * multiplier
                            else:
                                straddleSize = 0.0
                            lines.append(f"{nil_guard(player.name, 'unknown')}: raises {straddleSize - currentBet:.02f} to {straddleSize: .02f}")
                            currentBet = straddleSize
                            previous_action[nil_guard(player.id, "error")] = straddleSize

                        if line.contains("raises"):
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                self.seats[index].preFlopBet = True

                            raiseSize = float(last(line.replace(" and go all in", "").split("to ")) or "0.0") * multiplier
                            if isFirstAction:
                                lines.append(f"{nil_guard(player.name, 'unknown')}: bets {raiseSize:.02f}")
                                currentBet = raiseSize
                                isFirstAction = False
                            else:
                                lines.append(f"{nil_guard(player.name, 'unknown')}: "
                                             f"raises {raiseSize - currentBet:.02f} "
                                             f"to {raiseSize:.02f}")
                                currentBet = raiseSize
                            previous_action[nil_guard(player.id, "error")] = raiseSize

                        if line.contains("calls"):
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                self.seats[index].preFlopBet = True

                            callAmount = float(last(line.replace(" and go all in", "").split("calls ")) or "0.0")
                            callSize = callAmount * multiplier
                            if isFirstAction:
                                lines.append(f"{nil_guard(player.name, 'unknown')}: bets {callSize:.02f}")
                                currentBet = callSize
                                isFirstAction = False
                            else:
                                uncalledPortionOfBet = callSize - (previous_action[nil_guard(player.id, "error")] or 0.0)
                                lines.append(f"{nil_guard(player.name, 'unknown')}: calls {uncalledPortionOfBet:.02f}")
                            previous_action[nil_guard(player.id, "error")] = callSize

                        if line.contains("checks"):
                            lines.append(f"{nil_guard(player.name, 'unknown')}: checks")

                        if line.contains("folds"):
                            lines.append(f"{nil_guard(player.name, 'unknown')}: folds")
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                if (street_description == "before Flop") and not self.seats[index].preFlopBet:
                                    self.seats[index].summary = f"{nil_guard(player.name, 'Unknown')} folded {street_description} (didn't bet)"
                                else:
                                    self.seats[index].summary = f"{nil_guard(player.name, 'Unknown')} folded {street_description}"
                        
                        if line.contains("shows"):
                            handComponents = last(line.split("shows a "))
                            if handComponents is not None:
                                handComponents.replace(".", "").split(", ")
                            index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                            if index is not None:
                                self.seats[index].showedHand = handComponents and [EmojiCard(x).emojiFlip().value for x in handComponents]
                                lines.append(f"{player.name is not None or 'unknown'}: "
                                             f"shows [{' '.join([EmojiCard(x).emojiFlip().value for x in (handComponents or [])])}]")
                        
                        if line.contains("collected "):
                            # has showdown
                            if line.contains(" from pot with "):

                                winPotSize = last(line.split(" collected "))
                                if winPotSize is not None:
                                    winPotSize = float(nil_guard(first(winPotSize.split(" from pot with ")), "0.0")) * multiplier

                                # remove missing smalls -- poker stars doesnt do this?
                                winPotSize = winPotSize - self.small_blind_size * len(self.missingSmallBlinds) * multiplier

                                winDescription = last(line.split(" from pot with "))
                                if winDescription is not None:
                                    winDescription = nil_guard(first(winDescription.split(" (")), "error")
                                totalPotSize = winPotSize
                                if not self.printedShowdown:
                                    lines.append("*** SHOW DOWN ***")
                                    self.printedShowdown = True

                                lines.append(f"{nil_guard(player.name, 'Unknown')} collected {winPotSize:.02f} from pot")
                                
                                index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                                if index is not None:
                                    self.seats[index].summary = f"{nil_guard(player.name, 'Unknown')} showed [] and won ({winPotSize:.02f}) with {winDescription}"

                            else:
                                # no showdown
                                gainedPotSize = last(line.split(" collected "))
                                if gainedPotSize is not None:
                                    gainedPotSize = float(nil_guard(first(gainedPotSize.split(" from pot")), "0.0")) * multiplier
                                else:
                                    gainedPotSize = 0.0

                                # remove missing smalls -- poker stars doesnt do this?
                                gainedPotSize = gainedPotSize - self.small_blind_size * len(self.missingSmallBlinds) * multiplier

                                
                                if self.flop is None:
                                    preFlopAction = 0.0
                                    
                                    for player in self.players:
                                        preFlopAction = preFlopAction + (nil_guard(previous_action[nil_guard(player.id, "error")], 0.0))
                                    
                                    # catching edge case of folding around preflop
                                    if preFlopAction == float(self.big_blind_size + self.small_blind_size) * multiplier:
                                        gainedPotSize = float(self.small_blind_size) * multiplier
                                        lines.append(f"Uncalled bet ({self.big_blind_size * multiplier:.02f}) returned to {nil_guard(player.name< 'Unknown')}")
                                    else:
                                        if self.uncalledBet > 0:
                                            lines.append(f"Uncalled bet ({self.uncalled_bet * multiplier:.02f}) returned to {nil_guard(player.name, 'Unknown')}")
                                else:
                                    if self.uncalledBet > 0:
                                        lines.append(f"Uncalled bet ({self.uncalled_bet * multiplier:.02f}) returned to {nil_guard(player.name, 'Unknown')}")

                                totalPotSize = gainedPotSize
                                lines.append(f"{nil_guard(player.name, 'Unknown')} collected {gainedPotSize:.02f} from pot")
                                index = first([i for i,x in enumerate(self.seats) if x.player and x.player.id == player.id])
                                if index is not None:
                                    self.seats[index].summary = f"{nil_guard(player.name, 'Unknown')} collected ({gainedPotSize:.02f})"
                            
            
            if line.startswith("Uncalled bet"):
                uncalledString = first(line.split(" returned to"))
                if uncalledString is not None:
                    uncalledString = uncalledString.replace("Uncalled bet of ", "")
                try:
                    self.uncalled_bet = float(nil_guard(uncalledString, "0.0"))
                except:
                    self.uncalled_bet = 0.0
            
            if line.startswith("flop:"):
                lines.append(f"*** FLOP *** [{nil_guard(' '.join([x.value for x in (self.flop or [])]), 'error')}]")
                isFirstAction = True
                currentBet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0.0
                streetDescription = "on the Flop"

            if line.startswith("turn:"):
                lines.append(f"*** TURN *** [{nil_guard([' '.join(x.value for x in (self.flop or []))], 'error')}] "
                             f"[{nil_guard(self.turn and self.turn.value, 'error')}]")
                isFirstAction = True
                currentBet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0
                streetDescription = "on the Turn"

            if line.startswith("river:"):
                lines.append(f"*** RIVER *** [{nil_guard([' '.join(x.value for x in (self.flop or []))], 'error')} "
                             f"{nil_guard(self.turn and self.turn.value, 'error')}] "
                             f"[{nil_guard(self.river and self.river.value, 'error')}]")
                isFirstAction = True
                currentBet = 0
                for player in self.players:
                    previous_action[nil_guard(player.id, "error")] = 0.0

                streetDescription = "on the River"
            
            if self.lines.last == line:
                lines.append("*** SUMMARY ***")
                lines.append(f"Total pot: {totalPotSize:.02f)} | Rake 0")
                board: List[Card] = []
                board += nil_guard(self.flop, [])
                if self.turn: board.append(self.turn)
                if self.river: board.append(self.river)
                
                if board.count > 0:
                    lines.append(f"Board: [{' '.join([x.value for x in board])}]")

                for seat in self.seats:
                    summary = seat.summary
                    if self.dealer and self.player and self.dealer.id == seat.player.id:
                        # TODO: Not sure what this line does
                        summary = summary.replace(nil_guard(seat.player.name, "Unknown"), f"{nil_guard(seat.player.name, 'Unknown')} (button)")

                    if self.small_blind and seat.player and self.small_blind.id == seat.player.id:
                        summary = summary.replace(nil_guard(seat.player.name, "Unknown"), f"{nil_guard(seat.player.name, 'Unknown')} (small blind)")

                    for big_blind in self.big_blind:
                        if big_blind and seat.player and big_blind.id == seat.player.id:
                            summary = summary.replace(nil_guard(seat.player.name, "Unknown"), f"{nil_guard(seat.player.name, 'Unknown')} (big blind)")
                    
                    if seat.showedHand is not None and not summary.contains("[]"):
                        lines.append(f"Seat {seat.number}: {summary} [{nil_guard(seat.showed_hand, 'error')}]")
                    else:
                        summary = summary.replace("[]", f"[{nil_guard(seat.showed_hand, 'error')})]")
                        lines.append(f"Seat {seat.number}: {summary}")
                lines.append("")

        return lines
