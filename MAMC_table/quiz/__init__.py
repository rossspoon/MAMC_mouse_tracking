from otree.api import *
from time import time


doc = """
QUIZ
"""

def get_numbers():
    """
    Modify this function to generate the numbers.
    :return:  The return object is a dict where the key is the label and
                the value is a list of numbers for that table row.
    """
    return {"A": [50, 40, 30, 20, 100],
            "B": [52, 62, 35, 58, 8],
            "C": [48, 50, 61, 91, 90],
            "D": [51, 58, 69, 22, 3],
            "E": [45, 50, 50, 60, 50]}


class C(BaseConstants):
    NAME_IN_URL = 'quiztablemaker'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    choice = models.StringField()
    start_time = models.IntegerField(initial=-1)
    duration = models.IntegerField(initial=-1)

    numbers = models.StringField(blank=True)
    var_list = models.StringField(blank=True)

    def make_field(label, answer):
        return models.IntegerField(
            blank=False,
            label=label,
            widget=widgets.RadioSelect,
            choices=[
                [1, answer[0]],
                [2, answer[1]],
                [3, answer[2]],
                [4, answer[3]]]
        )


    q1 = make_field(label="If the mean of a Normal distribution is 20, where would the peak of the bell curve be? ",
                answer=['A. Above 20', 'B. Below 20', 'C. Exactly at 20', 'D. Do not know'])

    q2 = make_field(label="If I randomly choose 100 numbers from a normal distribution with mean 0 and very low variance and what do you think will be the average of these numbers?",
    answer=['A. Closee to 100',
            'B. Close to 10',
            'C. Close to 0',
            'D. Do not know'])
    q3 = make_field(label="The attributes will be picked from a Normal Distribution with mean 50 and different variances. What will be the order of decreasing variances? ",
    answer=['A. I > II > III > IV > V', 'B. V > IV > III > II > I', 'C. It will be random', 'D. I do not know'])


class TileClick(ExtraModel):
    player = models.Link(Player)
    seq = models.IntegerField()
    timestamp = models.IntegerField()
    x = models.IntegerField()
    y = models.IntegerField()


class OptionClick(ExtraModel):
    player = models.Link(Player)
    seq = models.IntegerField()
    timestamp = models.IntegerField()
    option = models.StringField()


def table_page_live_method(player, data):
    func = data.get('func')
    ts = round(time() * 1000)
    page_time = ts - player.start_time

    if func == 'tile-click':
        seq = data.get('seq')
        x = data.get('x')
        y = data.get('y')
        TileClick.create(player=player, seq=seq, timestamp=page_time, x=x, y=y)

    elif func == 'option-click':
        seq = data.get('seq')
        option = data.get('option')
        OptionClick.create(player=player, seq=seq, timestamp=page_time, option=option)


# PAGES

class Quiz(Page):
    form_model = 'player'
    form_fields = ['choice', 'q1', 'q2', 'q3']

    @staticmethod
    def vars_for_template(player: Player):
        if player.field_maybe_none('start_time') == -1:
            ts = round(time() * 1000)
            player.start_time = ts

        col_names=['Options/Attributes', 'I', 'II', 'III', 'IV', 'V']
        numbers = get_numbers()
        return dict(numbers=numbers,
                    column_names=col_names,
                    indexes=list(range(len(numbers))),
                    form_fields=['choice'],
                    )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            return

        ts = round(time() * 1000)
        player.duration = ts - player.start_time

    @staticmethod
    def js_vars(player: Player):
        # Number of clicks
        tile_click_order = len(TileClick.filter(player=player))
        opt_click_order = len(OptionClick.filter(player=player))
        return dict(tile_click_order=tile_click_order,
                    opt_click_order=opt_click_order)

    live_method = table_page_live_method


page_sequence = [Quiz]
