from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'information'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class InformationSheet(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1



page_sequence = [InformationSheet]
