from otree.api import *
import numpy as np

doc = """
Test app for generating the choice table.
"""


def get_numbers():
    my_list1 = np.random.normal(loc=50, scale=np.sqrt(10), size=5)
    my_list_round1 = np.round(my_list1).astype(int).tolist()

    my_list2 = np.random.normal(loc=50, scale=np.sqrt(100), size=5)
    my_list_round2 = np.round(my_list2).astype(int).tolist()

    my_list3 = np.random.normal(loc=50, scale=np.sqrt(200), size=5)
    my_list_round3 = np.round(my_list3).astype(int).tolist()

    my_list4 = np.random.normal(loc=50, scale=np.sqrt(300), size=5)
    my_list_round4 = np.round(my_list4).astype(int).tolist()

    my_list5 = np.random.normal(loc=50, scale=np.sqrt(400), size=5)
    my_list_round5 = np.round(my_list5).astype(int).tolist()

    """
    Modify this function to generate the numbers.
    :return:  The return object is a dict where the key is the label and
                the value is a list of numbers for that table row.
    """
    return {"A":  my_list_round1,
            "B":  my_list_round2,
            "C":  my_list_round3,
            "D":  my_list_round4,
            "E":  my_list_round5}

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
    form_model = 'player'
    form_fields = ['choice']

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
            TableClick.create(player=player, seq=seq, x=x, y=y)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        clicks = TableClick.filter(player=player)
        return dict(clicks=clicks)


page_sequence = [TablePage, Results]
