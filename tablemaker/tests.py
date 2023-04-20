from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):

    def play_round(self):

        if self.round_number == 1:
            yield IntroPage

        yield TablePage, dict(choice='A')
        yield Results
        try:
            print(f"Selected Round: {self.player.participant.BONUS_ROUND}")
        except:
            pass