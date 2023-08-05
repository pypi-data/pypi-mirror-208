import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from . import data


def extract_values_from_key(list_of_dicts, key):
    return [d[key] for d in list_of_dicts if key in d]


def count_days(start_date, end_date, business=True, calendar='anbima', holidays=[]):
    date_range = pd.date_range(start_date, end_date, freq='D')

    if business:
        if calendar is not None:
            calendar_holidays = data.holidays(calendar)
            calendar_holidays = extract_values_from_key(
                calendar_holidays, 'data')
            holidays.extend(calendar_holidays)

        holidays = pd.to_datetime(holidays)
        weekdays = np.isin(date_range.weekday, [5, 6], invert=True)
        non_holidays = np.isin(date_range, holidays, invert=True)
        valid_days = np.logical_and(weekdays, non_holidays).sum()
    else:
        valid_days = len(date_range)

    return valid_days


def add_days(start_date, num_days=0, num_months=0, num_years=0, business=True, calendar='anbima', holidays=[]):
    date_format = "%Y-%m-%d"
    start_date = datetime.strptime(start_date, date_format)

    if calendar is not None:
        calendar_holidays = data.holidays(calendar)
        calendar_holidays = extract_values_from_key(
            calendar_holidays, 'data')
        holidays.extend(calendar_holidays)

    holidays = [datetime.strptime(h, date_format) for h in holidays]

    new_date = start_date + \
        relativedelta(days=num_days, months=num_months, years=num_years)

    if business:
        while new_date.weekday() in (5, 6) or new_date in holidays:
            new_date += timedelta(days=1)

    return new_date.strftime(date_format)
