from otree.api import *
from time import time


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
            "D": [12, 58, 39, 22, 73],
            "E": [50, 50, 50, 50, 50]}


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
    form_fields = ['choice']

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
