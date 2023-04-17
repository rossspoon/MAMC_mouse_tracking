import statsmodels.sandbox.distributions.extras
from otree.api import *
import numpy as np
from time import time
import random
import roman
import json
import os

doc = """
Test app for generating the choice table.
"""

VAR_LIST = [10, 100, 200, 300, 400]

def get_attr_values(v, n):
    return np.random.normal(loc=50, scale=np.sqrt(v), size=n).astype(int)


def sample_var_list(variances=VAR_LIST):
    va = random.sample(variances, 5)
    return va


def get_col_names(variances=VAR_LIST):
    var_dict = {v: roman.toRoman(i) for i, v in enumerate(sorted(variances), start=1)}
    col_names = ["Options/Attributes"] + [var_dict[v] for v in variances]
    return col_names


def get_numbers(labels=["A", "B", "C", "D", "E"], variances=VAR_LIST):
    """
    Modify this function to generate the numbers.
    :return:  The return object is a dict where the key is the label and
                the value is a list of numbers for that table row.
    """
    num_attrs = 5
    num_options = len(labels)

    # Loop over the variances and generate the values for each one.
    # This particular syntax is called a list comprehension
    #  it is quite useful for transforming an iterable of one thing into another.
    # Here we are transforming the list of variances into a list of lists of the
    # random attribute values.
    number_lists = [get_attr_values(v, num_options) for v in variances]

    # As you thought to do, I'm transposing the matrix.
    # First the concatenate function joins all the lists from number_list into
    # one long list.
    # Then I reshape the list into the 5x5 matrix of values.  Then transpose it.
    matrix = np.concatenate(number_lists).reshape((num_attrs, num_options)).T

    # Like this list comprehension above, the dict comprehension can transform one
    # iterable into another.   Here, I'm changing a list of integers (the range function)
    # into the return map of {<LABEL>:  <ATTRIBUTE_VALUES>}
    ret_val = {labels[i]: matrix[i, :].tolist() for i in range(num_options)}

    # Uncomment here to check that the "columns" of the
    # returned dict match up with the "rows" of the
    # that we generated randomly
    # print(ret_val)
    # print(number_lists[4])

    return ret_val

num_rounds = os.getenv('NUM_ROUNDS')
if not num_rounds:
    num_rounds = 40

class C(BaseConstants):
    NAME_IN_URL = 'tablemaker'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = int(num_rounds)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    choice = models.StringField(blank=True)
    choice_value = models.IntegerField(blank=True)
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



def get_payout(player):
    players = player.in_all_rounds()
    values = [p.field_maybe_none('choice_value') for p in players if p.field_maybe_none('choice_value')]

    if len(values) == 0:
        return None

    return random.choice(values)

# PAGES

class TablePage(Page):
    form_model = 'player'
    form_fields = ['choice']
    timeout_seconds = 15

    @staticmethod
    def vars_for_template(player: Player):
        if player.field_maybe_none('start_time') == -1:
            ts = round(time() * 1000)
            player.start_time = ts

        # retrieve the var_list or create a new one
        var_list_raw = player.field_maybe_none('var_list')
        if var_list_raw:
            var_list = json.loads(var_list_raw)
        else:
            var_list = sample_var_list()
            player.var_list = json.dumps(var_list)

        # retrieve number grid or create a new one
        numbers_raw = player.field_maybe_none('numbers')
        if numbers_raw:
            numbers = json.loads(numbers_raw)
        else:
            numbers = get_numbers(variances=var_list)
            player.numbers = json.dumps(numbers)

        # generate col_names from the var_list
        col_names = get_col_names(variances=var_list)

        return dict(numbers=numbers,
                    column_names=col_names,
                    indexes=list(range(len(numbers))),
                    form_fields=['choice'],
                    )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):

        # calculate payout
        if player.round_number == C.NUM_ROUNDS:
            payout = get_payout(player)
            if payout:
                player.participant.payoff = payout

        # if timeout, nothing else to do
        if timeout_happened:
            return

        # Record Duration - Time to click
        ts = round(time() * 1000)
        player.duration = ts - player.start_time

        # Tabulate the value of the choice
        numbers = json.loads(player.numbers)
        choice = player.field_maybe_none('choice')
        if choice:
            player.choice_value = sum(numbers[choice])

    @staticmethod
    def js_vars(player: Player):
        # Number of clicks
        tile_click_order = len(TileClick.filter(player=player))
        opt_click_order = len(OptionClick.filter(player=player))
        return dict(tile_click_order=tile_click_order,
                    opt_click_order=opt_click_order)

    live_method = table_page_live_method

    @staticmethod
    def error_message(player, values):
        c = values['choice']
        if not c:
            return "Please select and option"


class Results(Page):
    timeout_seconds = 15

    @staticmethod
    def vars_for_template(player: Player):
        tile_clicks = TileClick.filter(player=player)
        opt_clicks = OptionClick.filter(player=player)
        return dict(tile_clicks=tile_clicks, opt_clicks=opt_clicks)



page_sequence = [TablePage, Results]
