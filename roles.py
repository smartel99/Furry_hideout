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
