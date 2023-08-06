import os

client_id = os.environ['polar_client_id']
client_secret = os.environ['polar_client_secret']

AUTHORIZE_URL = 'https://auth.polar.com/oauth/authorize'
ACCESS_TOKEN_URL = 'https://auth.polar.com/oauth/token'
AUTHORIZE_PARAMS = {'client_id': client_id,
                    'response_type': 'code',
                    'scope': 'team_read'}

positions = {'Martin Frese': 'Wingback',
             'Ivan Mesik': 'Centerback',
             'Jacob Steen Christensen': 'Central Midfielder',
             'Joachim Rothmann': 'Striker',
             'Lucas Lykkegaard': 'Wingback',
             'Emeka Nnamani': 'Striker',
             'Tochi Chukwuani': 'Central Midfielder',
             'Ibrahim Abu': 'Striker',
             'Maxwell Woledzi': 'Centerback',
             'Oliver Antmann': 'Striker',
             'Simon Adingra': 'Striker',
             'Jonas Jensen-Abbew': 'Centerback',
             'Andreas Bredahl Pedersen': 'Striker',
             'Ernest Appiah': 'Wingback',
             'Jesper Dickman': 'Winger',
             'Leo Walta': 'Central Midfielder',
             'Kian Hansen': 'Centerback',
             'Magnus Kofod': 'Central Midfielder',
             'Mads Thychosen': 'Centerback',
             'Jonathan Amon': 'Striker',
             'Oliver Villadsen': 'Wingback',
             'Abu Francis': 'Central Midfielder',
             'Lasso Coulibaly': 'Central Midfielder',
             'Mohammed Diomande': 'Central Midfielder',
             'Adamo Nagalo': 'Centerback',
             'Daniel Svensson': 'Wingback',
             'Andreas Schjelderup': 'Striker'}
