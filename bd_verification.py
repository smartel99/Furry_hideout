import datetime

from dateutil import parser


def verify_birthday(date):
    bd = parser.parse(date)
    today = datetime.datetime.now()
    age = divmod(((today - bd).total_seconds()), 31556926)[0]  # Gets the time difference in seconds then converts it
    # in years
    if age < 18:
        raise Underaged("You must be 18 or older to access this server.\n"
                        "If this is an error, you can re-join the server")
    elif age > 50:
        raise Invalid("For reasons of safety, dates more than 50 years ago are invalid")


class Underaged(Exception):
    def __init__(self, message):
        self.message = message


class Invalid(Exception):
    def __init__(self, message):
        self.message = message
