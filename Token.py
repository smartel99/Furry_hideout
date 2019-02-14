import os


def get_token_file():
    return os.path.abspath(os.path.join('..', 'FH_data', 'bot.token'))


def get_token():
    file = get_token_file()
    with open(file, 'r') as fin:
        token = fin.readline()
    return token


def get_log_path(message):
    path = os.path.abspath(os.path.join('..', 'FH_data', message.guild.name))
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.abspath(os.path.join('..', 'FH_data', message.guild.name, message.author.name + '.user'))
