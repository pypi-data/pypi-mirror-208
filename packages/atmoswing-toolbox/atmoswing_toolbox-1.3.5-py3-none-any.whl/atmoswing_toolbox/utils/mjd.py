import datetime

import numpy as np
import pandas as pd


def as_mjd(year, month, day, hour=0, minute=0):
    date = datetime.datetime(year, month, day, hour, minute)
    return pd.DatetimeIndex([date]).to_julian_date() - 2400000.5


def date_as_mjd(date):
    return pd.DatetimeIndex(date).to_julian_date() - 2400000.5


def jd_to_date(jd):
    """
    Transform julian date numbers to year, month and day (array-based).
    From https://gist.github.com/jiffyclub/1294443
    """
    jd = jd + 0.5

    f, i = np.modf(jd)
    i = i.astype(int)

    a = np.trunc((i - 1867216.25) / 36524.25)
    b = np.zeros(len(jd))

    idx = tuple([i > 2299160])
    b[idx] = i[idx] + 1 + a[idx] - np.trunc(a[idx] / 4.)
    idx = tuple([i <= 2299160])
    b[idx] = i[idx]

    c = b + 1524
    d = np.trunc((c - 122.1) / 365.25)
    e = np.trunc(365.25 * d)
    g = np.trunc((c - e) / 30.6001)

    day = c - e + f - np.trunc(30.6001 * g)

    month = np.zeros(len(jd))
    month[g < 13.5] = g[g < 13.5] - 1
    month[g >= 13.5] = g[g >= 13.5] - 13
    month = month.astype(int)

    year = np.zeros(len(jd))
    year[month > 2.5] = d[month > 2.5] - 4716
    year[month <= 2.5] = d[month <= 2.5] - 4715
    year = year.astype(int)

    return year, month, day


def days_to_hours_mins(days):
    """Transform a number of days to hours and minutes"""
    hours = days * 24.
    hours, hour = np.modf(hours)

    minutes = hours * 60.
    _, minute = np.modf(minutes)

    return hour.astype(int), minute.astype(int)


def mjd_to_datetime(mjd):
    """Transform modified julian dates to datetime instances (array-based)."""
    jd = mjd + 2400000.5
    year, month, day = jd_to_date(jd)

    frac_days, day = np.modf(day)
    day = day.astype(int)

    hour, minute = days_to_hours_mins(frac_days)

    date = np.empty(len(mjd), dtype='datetime64[s]')

    for idx, _ in enumerate(year):
        date[idx] = datetime.datetime(year[idx], month[idx], day[idx],
                                      hour[idx], minute[idx], 0, 0)

    return date
