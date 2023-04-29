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

VAR_LIST = [600, 300, 200, 100, 10]

# Assign treatments.  This is based off
# of the id_in_group value of the player.
# Even ids are not control and odds are.
def creating_session(subsession):
    for p in subsession.get_players():
        is_control = p.id_in_group % 2
        p.is_control = is_control


def get_attr_values(v, n):
    return np.random.normal(loc=50, scale=np.sqrt(v), size=n).astype(int)


def sample_var_list(variances=VAR_LIST):
    va = random.sample(variances, 5)
    return va


def get_col_names(variances=VAR_LIST):
    var_dict = {v: roman.toRoman(i) for i, v in enumerate(reversed(sorted(variances)), start=1)}
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
    choice_value = models.IntegerField(initial=0)
    start_time = models.StringField()
    duration = models.IntegerField(initial=-1)
    is_control = models.BooleanField(initial=False)

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

    # inexplicable exception getting thrown here.
    # catching it and using a safe default.
    try:
        start_time = int(player.start_time)
        page_time = ts - start_time
    except TypeError:
        page_time = -1

    if func == 'tile-click':
        seq = data.get('seq')
        x = data.get('x')
        y = data.get('y')
        TileClick.create(player=player, seq=seq, timestamp=page_time, x=x, y=y)

    elif func == 'option-click':
        seq = data.get('seq')
        option = data.get('option')
        OptionClick.create(player=player, seq=seq, timestamp=page_time, option=option)



def select_random_round(player):
    all_rounds = player.in_all_rounds()
    players = [p for p in all_rounds if p.choice_value]
    if len(players) == 0:
        return None

    selected_player = random.choice(players)
    return selected_player

# PAGES

class TablePage(Page):
    form_model = 'player'
    form_fields = ['choice']
    timeout_seconds = 15

    @staticmethod
    def vars_for_template(player: Player):
        if player.field_maybe_none('start_time') is None:
            ts = round(time() * 1000)
            player.start_time = str(ts)

        # retrieve the var_list or create a new one
        var_list_raw = player.field_maybe_none('var_list')
        if var_list_raw:
            var_list = json.loads(var_list_raw)
        else:
            # Here we generate the column list for the player
            # control players do not get a scrambled list.
            if player.is_control:
                var_list = VAR_LIST
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

        # if timeout, nothing else to do
        if not timeout_happened:
            # Record Duration - Time to click
            ts = round(time() * 1000)
            start_time = int(player.start_time)
            player.duration = ts - start_time


        # Tabulate the value of the choice
        # we will count their last option selected as a choice
        # even if they don't submit it by clicking "Next"
        numbers = json.loads(player.numbers)
        choice = player.field_maybe_none('choice')
        if choice:
                player.choice_value = sum(numbers[choice])

        # calculate payout
        if player.round_number == C.NUM_ROUNDS:
            random_p = select_random_round(player)
            if random_p:
                participant = player.participant
                participant.payoff = random_p.choice_value
                participant.BONUS_ROUND = random_p.field_maybe_none('round_number')
                participant.BONUS_NUMBERS = random_p.field_maybe_none('numbers')
                labels_raw = random_p.field_maybe_none('var_list')
                if labels_raw:
                    labels = get_col_names(variances=json.loads(labels_raw))
                    participant.BONUS_LABELS = labels
                participant.BONUS_CHOICE = random_p.field_maybe_none('choice')
            else:
               player.participant.payoff = 0


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

class IntroPage(Page):
    timeout_seconds = 30

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

def custom_export(players):
    # header row
    yield ['session', 'participant_code', 'round_number',
           'type', 'time', 'seq', 'x', 'y', 'option']

    for p in players:
        participant = p.participant
        session = p.session

        for tc in TileClick.filter(player=p):
            ts = tc.timestamp
            x = tc.x
            y = tc.y
            yield [session.code, participant.code, p.round_number,
                    'tile', ts, tc.seq, x, y, '']

        for oc in OptionClick.filter(player=p):
            ts = oc.timestamp
            option = oc.option
            yield [session.code, participant.code, p.round_number,
                   'option', ts, oc.seq, '', '', option]


page_sequence = [IntroPage, TablePage, Results]
