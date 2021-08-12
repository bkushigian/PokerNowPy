import csv
from game import Game
from argparse import ArgumentParser
from typing import List, Dict, Optional

class PN2PS:
    def __init__(self):
        self.parser = ArgumentParser()
        self.parser.add_argument("heroname", help="Your name in log")
        self.parser.add_argument("--table_url", default=None, help="PokerNow Table URL to download")
        self.parser.add_argument("--filename", default=None, help="PokerNow log filename")
        self.parser.add_argument("--limit", type=int, default=-1, help="Limit amount of hands processed")
        self.parser.add_argument("--multiplier", type=float, default=1.0, help="Multiply bet amounts by given value")
        self.parser.add_argument("--name", default="DGen", type=str, help="Table name")
        self.parser.add_argument("--output", "-o", default=None, help="File to write to (instead of stdout)")
        self.parser.add_argument("--debug", "-d", action="store_true", help="print debug output")
        args = self.parser.parse_args()

        self.heroname = args.heroname
        self.table_url = args.table_url
        self.filename = args.filename
        self.limit = args.limit
        self.multiplier = args.multiplier
        self.name = args.name
        self.output_file = args.output
        self.debug =args.debug

    def process_csv(self, csv_rows: List[Dict[str, str]]):
        game = Game(csv_rows, debug_hand_action=self.debug)


        if self.output_file is None:
            for hand in game.hands[:self.limit]:
                hand.printPokerStarsDescription(hero_name=self.heroname, multiplier=self.multiplier or 1.0, table_name = self.name or "DGen")
        else:
            with open(self.output_file, 'w+', encoding='utf-8') as f:
                limit = len(game.hands)
                if self.limit > 0:
                    limit = self.limit
                for hand in game.hands[:limit]:
                    descr = hand.getPokerStarsDescription(hero_name=self.heroname, multiplier=self.multiplier or 1.0, table_name = self.name or "DGen")
                    f.write(descr)

    def run(self):
        if self.filename:
            self.process_csv(read_csv_as_dict(self.filename))
        elif self.table_url:
            raise RuntimeError("table url is not implemented")
        else:
            print("No log data provided...please specify --filename")


def read_csv_as_dict(file: str) -> Optional[List[Dict[str, str]]]:
    with open(file, 'r', encoding='utf-8') as f:
        try:
            return list(csv.DictReader(f))
        except:
            return None

if __name__ == '__main__':
    PN2PS().run()