from otree.api import *


doc = """
Test app for generating the choice table.
"""

def get_numbers():
    """
    Modify this function to generate the numbers.
    :return:  The return object is a dict where the key is the label and
                the value is a list of numbers for that table row.
    """
    return {"A": [45, 29, 30, 10, 38],
            "B": [84, 92, 13, 28, 38],
            "C": [33, 29, 61, 91, 58],
            "D": [12, 58, 39, 22, 73]}



class C(BaseConstants):
    NAME_IN_URL = 'tablemaker'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    choice = models.StringField();


class TableClick(ExtraModel):
    player = models.Link(Player)
    seq = models.IntegerField()
    x = models.IntegerField()
    y = models.IntegerField()


# PAGES
class TablePage(Page):
    form_model='player'
    form_fields=['choice']

    @staticmethod
    def vars_for_template(player: Player):
        numbers = get_numbers()
        return dict(numbers=numbers,
                    indexes=list(range(len(numbers))),
                    form_fields=['choice'],
                    )

    @staticmethod
    def live_method(player, data):
        func = data.get('func')
        if func == 'cell-click':
            seq = data.get('seq')
            x = data.get('x')
            y = data.get('y')
            TableClick.create(player=player, seq=seq,  x=x, y=y)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        clicks = TableClick.filter(player=player)
        return dict(clicks = clicks)

page_sequence = [TablePage, Results]
