from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'instructions'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class Instructions(Page):
    pass

class Instructionspg2(Page):
    pass

class Instructionspg3(Page):
    pass



page_sequence = [Instructions, Instructionspg2, Instructionspg3]
