from os import environ

SESSION_CONFIGS = [
    # dict(
    #     name='public_goods',
    #     app_sequence=['public_goods'],
    #     num_demo_participants=3,
    # ),

dict(name='full_experiment',
     app_sequence=['information','instructions','quiz','tablemaker','tablemakercontrol','survey'],
     num_demo_participants=1),

dict(name='information',
     app_sequence=['information'],
     num_demo_participants=1),

dict(name='instructions',
     app_sequence=['instructions'],
     num_demo_participants=1),

dict(name='quiz',
     app_sequence=['quiz'],
     num_demo_participants=1),

dict(name='tablemaker',
     app_sequence=['tablemaker'],
     num_demo_participants=1),

dict(name='tablemakercontrol',
     app_sequence=['tablemakercontrol'],
     num_demo_participants=1),

dict(name='survey',
     app_sequence=['survey'],
     num_demo_participants=1)
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.01, participation_fee=2.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '5215598735434'
