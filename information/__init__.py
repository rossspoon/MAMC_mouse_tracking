from otree.api import *


doc = """
Show information sheet and get consent.
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
    consent_given = models.BooleanField()


# PAGES
class InformationSheet(Page):
    form_model = Player
    form_fields = ['consent_given']

class ConsentDeniedPage(Page):

    @staticmethod
    def is_displayed(player: Player):
        return not player.consent_given

page_sequence = [InformationSheet, ConsentDeniedPage]
