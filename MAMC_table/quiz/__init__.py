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
    return {"A": [50, 40, 30, 20, 90],
            "B": [52, 62, 35, 58, 8],
            "C": [48, 50, 61, 91, 100],
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
    is_understand = models.BooleanField(initial=True)

    def make_field(label, answer):
        return models.IntegerField(
            blank=True,
            label=label,
            #widget=widgets.RadioSelect,
            choices=[
                [1, answer[0]],
                [2, answer[1]],
                [3, answer[2]],
                [4, answer[3]]]
        )


    q1 = make_field(label="If the mean of a Normal distribution is 20, where would the peak of the bell curve be? ",
                answer=['A. Above 20', 'B. Below 20', 'C. Exactly at 20 ', 'D. Do not know'])

    q2 = make_field(label="If I randomly choose 100 numbers from a normal distribution with mean 0 and very low variance and what do you think will be the average of these numbers?",
    answer=['A. Close to 100',
            'B. Close to 10',
            'C. Close to 0',
            'D. Do not know'])
    q3 = make_field(label="The attributes will be picked from a Normal Distribution with mean 50 and different variances. What will be the order of decreasing variances? ",
    answer=['A. I > II > III > IV > V', 'B. V > IV > III > II > I', 'C. It will be random', 'D. I do not know'])

    choice_score = models.BooleanField(blank=True)
    q1_score = models.BooleanField(blank=True)
    q2_score = models.BooleanField(blank=True)
    q3_score = models.BooleanField(blank=True)

# HELPER FUNCTIONS

def get_messages(player: Player):
    ret = {'q1': "" if player.q1_score else "The bell curve will peak exactly at 20.",
           'q2': "" if player.q2_score else f'The average of 100 draws will typically be very close to the mean.  In this case, zero.',
           'q3': "" if player.q3_score else f'The attribute (column) with the highest variance will be labeled IV.  The lowest'+
                                            f' variance attribute will be labeled I',
           }
    return ret



# PAGES

class Quiz(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3']

    @staticmethod
    def error_message(player: Player, values):
        solutions = dict(choice=3, q1=3, q2=3, q3=2)

        if values != solutions:
            player.is_understand = False


    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Grade the quiz
        player.q1_score = player.field_maybe_none('q1') == 3
        player.q2_score = player.field_maybe_none('q2') == 3
        player.q3_score = player.field_maybe_none('q3') == 2


class QuizResults(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3']

    @staticmethod
    def vars_for_template(player: Player):

        col_names=['Options/Attributes', 'I', 'II', 'III', 'IV', 'V']
        numbers = get_numbers()
        return dict(numbers=numbers,
                    column_names=col_names,
                    indexes=list(range(len(numbers))),
                    form_fields=['choice'],
                    )


    @staticmethod
    def js_vars(player: Player):
        success = False

        fields_to_check = {f: f"{f}_score" for f in ['q1', 'q2', 'q3']}
        scored = {f: bool(player.field_maybe_none(s)) for f, s in fields_to_check.items()}
        question_class = {n: 'correct' if b else 'wrong' for n, b in scored.items()}

        # This variable will signal the js to turn the error message green.
        success = all(scored.values())


        return {'q_class': question_class,
                'success': success,
                'errors': get_messages(player)}


class Practice(Page):
    form_model = 'player'
    form_fields = ['choice']
    timeout_seconds = 300

    @staticmethod
    def vars_for_template(player: Player):
        col_names = ['Options/Attributes', 'I', 'II', 'III', 'IV', 'V']
        numbers = get_numbers()
        return dict(numbers=numbers,
                    column_names=col_names,
                    indexes=list(range(len(numbers))),
                    form_fields=['choice'],
                    )


class PracticeResults(Page):
    @staticmethod
    def vars_for_template(player: Player):
        totals = {key: sum(n) for key, n in get_numbers().items()}
        correct = player.field_maybe_none('choice') == 'C'
        return dict(totals=totals, correct=correct)

    @staticmethod
    def js_vars(player: Player):
        return dict(choice=player.field_maybe_none('choice'))

page_sequence = [Quiz, QuizResults, Practice, PracticeResults]
