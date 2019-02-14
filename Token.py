import os


def get_token_file():
    return os.path.abspath(os.path.join('..', 'FH_data', 'bot.token'))


def get_token():
    file = get_token_file()
    with open(file, 'r') as fin:
        token = fin.readline()
    return token
