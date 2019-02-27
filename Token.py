import os


def get_token_file():
    return os.path.abspath(os.path.join('..', 'FH_data', 'bot.token'))


def get_token():
    file = get_token_file()
    with open(file, 'r', encoding="utf-8") as fin:
        token = fin.readline()
    return token


def get_log_path(message):
    path = os.path.abspath(os.path.join('..', 'FH_data', message.guild.name, message.author.name))
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.abspath(os.path.join('..', 'FH_data', message.guild.name,
                                        message.author.name,
                                        message.author.name + ".user"))


def get_attachment_file_path(message, a):
    path = os.path.abspath(os.path.join('..', 'FH_data', message.guild.name, message.author.name))
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.abspath(os.path.join('..', 'FH_data', message.guild.name,
                                        message.author.name,
                                        "attachment_{}.".format(str(a.id) + "." + get_file_type(a.url))))
    return path


def get_file_type(url):
    r = url.split("/")
    r = r[-1]
    return r.split(".")[-1]


def get_logging_file():
    path = os.path.abspath(os.path.join('..', 'FH_data'))
    if not os.path.exists(path):
        os.makedirs(path)
    return path + "/bot.log"
