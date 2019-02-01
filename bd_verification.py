import datetime

from dateutil import parser


def verify_birthday(date):
    bd = parser.parse(date)
    today = datetime.datetime.now()
    age = divmod(((today - bd).total_seconds()), 31556926)[0]  # Gets the time difference in seconds then converts it
    # in years
    if age < 18:
        raise Underaged("You must be 18 or older to access this server")


class Underaged(Exception):
    def __init__(self, message):
        self.message = "User must be over 18"

    def __str__(self):
        return self.message
