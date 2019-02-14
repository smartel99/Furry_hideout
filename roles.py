import json
import os
import re

import custom_react
import merge


def get_path_of_file():
    return os.path.abspath(os.path.join('..', 'FH_data', 'role_data.json'))


def save_roles(data):
    with open(get_path_of_file(), 'w') as fout:
        fout.write(json.dumps(data, indent=4))


def load_roles():
    try:
        with open(get_path_of_file(), 'rt') as fin:
            r = json.loads(fin.read())
            print(r)
            return r
    except FileNotFoundError:
        print("Created 'role_data.json'")
        save_roles([])
        return load_roles()


role_data = [{'guild': 'bot fuck',
              'roles': [{
                  'message_id': 543168331608358929,
                  'category': 'Orientation',
                  'roles': [{
                      'name': 'Heterosexual',
                      'emoji': '1⃣'},
                      {'name': 'Homosexual',
                       'emoji': '2⃣'},
                      {'name': 'Bisexual',
                       'emoji': '3⃣'},
                      {'name': 'Pansexual', 'emoji': '4⃣'},
                      {'name': 'Demisexual', 'emoji': '5⃣'}
                  ]
              }]
              }]
print(role_data)


def get_role_category(role):
    if role == "Male" or role == "Female" or role == "Gender Fluid" or role == "Transgender":
        return "Gender"
    elif role == "Heterosexual" or role == "Homosexual" or role == "Bisexual" or role == "Pansexual" or role == "Demisexual":
        return "Orientation"
    elif role == "Dominant" or role == "Submissive" or role == "Switch":
        return "Preference"
    else:
        return None


def user_has_role_in_same_category(user, role):
    r_cat = get_role_category(role.name)
    for r in user.roles:
        if r_cat == get_role_category(r.name):
            return True
    return False


def add_roles_to_data(d):
    global role_data

    print(merge.merge(role_data, d))


def extract_roles_from_message(message):
    d = [{"guild": message.guild.name,
          "roles": [
              {"message_id": message.id,
               "category": message.content.split('\n')[1],
               "roles": []}
          ]}]
    for idx, r in enumerate(re.findall("\[(.+?)]", message.content)):
        d[0]["roles"][0]["roles"].append({"name": r,
                                          "emoji": custom_react.reations[idx + 1]})
    print(d)
    add_roles_to_data(d)
