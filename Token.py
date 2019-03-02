import os


def get_token_file():
    return os.path.abspath(os.path.join('..', 'FH_data', 'bot.token'))


def get_token():
    file = get_token_file()
    with open(file, 'r', encoding="utf-8") as fin:
        token = fin.readline()
    return token


def get_log_path(message):
    path = os.path.abspath(os.path.join('..', 'FH_data', message.guild.name, message.author.name.replace(".", "")))
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.abspath(os.path.join('..', 'FH_data', message.guild.name,
                                        message.author.name.replace(".", ""),
                                        message.author.name.replace(".", "") + ".user"))


def get_attachment_file_path(message, a):
    path = os.path.abspath(os.path.join('..', 'FH_data', message.guild.name, message.author.name.replace(".", "")))
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.abspath(os.path.join('..', 'FH_data', message.guild.name,
                                        message.author.name.replace(".", ""),
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


def get_zip_path():
    path = os.path.abspath(os.path.join('..', 'FH_data'))
    if not os.path.exists(path):
        os.makedirs(path)
    return path + "/user.zip"


def get_user_folder(user_name, guild_name):
    path = os.path.abspath(os.path.join('..', 'FH_data', guild_name, user_name.replace(".", "")))
    if not os.path.exists(path):
        return None
    else:
        return path


def get_files_in_user_folder(user_name, guild_name) -> list:
    folder = get_user_folder(user_name, guild_name)
    r = []
    if not folder:
        return []
    items = os.listdir(folder)

    for item in items:
        full_item = os.path.join(folder, item)
        if not os.path.isdir(full_item):
            r.append(full_item)
    return r


def get_file_name_from_path(path):
    import ntpath
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
