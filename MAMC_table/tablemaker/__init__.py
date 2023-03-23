from otree.api import *
import numpy as np

doc = """
Test app for generating the choice table.
"""


def get_attr_values(v, n):
    return np.random.normal(loc=50, scale=np.sqrt(v), size=n).astype(int)

def get_numbers():
    """
    Modify this function to generate the numbers.
    :return:  The return object is a dict where the key is the label and
                the value is a list of numbers for that table row.
    """

    variances = [10, 100, 200, 300, 400]
    labels = ["A", "B", "C", "D", "E"]
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
