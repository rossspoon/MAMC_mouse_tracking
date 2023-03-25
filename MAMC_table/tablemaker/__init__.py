from otree.api import *
import numpy as np
from time import time

doc = """
Test app for generating the choice table.
"""


def get_attr_values(v, n):
    return np.random.normal(loc=50, scale=np.sqrt(v), size=n).astype(int)

def get_numbers(variances=[10, 100, 200, 300, 400], labels=["A", "B", "C", "D", "E"]):
    """
    Modify this function to generate the numbers.
    :return:  The return object is a dict where the key is the label and
                the value is a list of numbers for that table row.
    """

    num_attrs = len(variances)
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
    #print(ret_val)
    #print(number_lists[4])

    return ret_val



class C(BaseConstants):
    NAME_IN_URL = 'tablemaker'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    choice = models.StringField()
    start_time = models.IntegerField(initial=-1)
    duration = models.IntegerField(initial=-1)


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
    if func == 'tile-click':
        seq = data.get('seq')
        ts = data.get('ts')
        x = data.get('x')
        y = data.get('y')
        TileClick.create(player=player, seq=seq, timestamp=ts, x=x, y=y)

    elif func == 'option-click':
        seq = data.get('seq')
        ts = data.get('ts')
        option = data.get('option')
        OptionClick.create(player=player, seq=seq, timestamp=ts, option=option)


# PAGES
class TablePage(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def vars_for_template(player: Player):
        # record the start time
        player.start_time = round(time() * 1000)

        numbers = get_numbers()
        return dict(numbers=numbers,
                    form_fields=['choice'],
                    )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            return

        ts = round(time() * 1000)
        player.duration = ts - player.start_time

    live_method = table_page_live_method



class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        tile_clicks = TileClick.filter(player=player)
        opt_clicks = OptionClick.filter(player=player)
        return dict(tile_clicks=tile_clicks, opt_clicks=opt_clicks)


page_sequence = [TablePage, Results]
