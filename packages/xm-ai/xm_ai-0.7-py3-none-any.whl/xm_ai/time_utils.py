from datetime import date, timedelta, datetime

today = date.today()
date_string_pattern = "%b-%d-%Y"


def week_ago(a_date):
    return a_date - timedelta(7)


def convert_to_datetime_obj(string_date):
    return datetime.strptime(string_date, date_string_pattern).date()


def convert_datetime_obj_to_string(datetime_object):
    return datetime_object.strftime(date_string_pattern)


def compare_dates(a_date, date_as_string):
    # Convert the string_date to a datetime object
    string_date = convert_to_datetime_obj(date_as_string)

    # Compare the two dates
    return a_date > string_date
