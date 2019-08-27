import datetime as dt
from copy import deepcopy

BEGIN=dt.datetime(year=1970,month=1,day=1)
END=dt.datetime(year=2030,month=1,day=1)
DAY=dt.timedelta(days=1)

def date_range(begin,end):

    d=deepcopy(begin)
    rng=[d]

    while d <= end:

        d+=DAY

        rng.append(d)

    return rng

def date_int(date):

    return int(f'{date.year}'+'{0:0=2d}'.format(date.month)+'{0:0=2d}'.format(date.day))


def date_string(date):

    return date.strftime("%Y-%m-%d")


def date_to_month(date):

    return dt.datetime(year=date.year,month=date.month,day=1)

DATE_RANGE=date_range(BEGIN,END)
DATE_TO_INT_CACHE={}
INT_TO_DATE_CACHE={}
DATE_TO_STRING_CACHE={}

for date in DATE_RANGE:

    dateString=date_string(date)
    dateInt=date_int(date)

    DATE_TO_INT_CACHE[dateString]=dateInt
    INT_TO_DATE_CACHE[dateInt]=dateString
    DATE_TO_STRING_CACHE[date]=dateString


def from_cache(x,cache):

    return cache[x]


def date_string_to_int(dateString):

    return from_cache(dateString,DATE_TO_INT_CACHE)


def date_to_date_string(dateString):

    return from_cache(dateString,DATE_TO_STRING_CACHE)


def int_to_date_string(dateInt):

    return from_cache(dateInt,INT_TO_DATE_CACHE)


MONTH_TO_INT_CACHE={}
INT_TO_MONTH_CACHE={}
DATE_STRING_TO_MONTH_STRING_CACHE={}

for date in DATE_RANGE:

    month=date_to_month(date)
    dateString=date_to_date_string(date)
    monthString=date_string(month)
    monthInt=date_string_to_int(monthString)
    
    MONTH_TO_INT_CACHE[monthString]=monthInt
    INT_TO_MONTH_CACHE[monthInt]=monthString
    DATE_STRING_TO_MONTH_STRING_CACHE[dateString]=monthString


def month_string_to_int(monthString):

    return from_cache(monthString,MONTH_TO_INT_CACHE)


def int_to_month_string(monthInt):

    return from_cache(monthInt,INT_TO_MONTH_CACHE)


def date_string_to_month_string(dateString):

    return from_cache(dateString,DATE_STRING_TO_MONTH_STRING_CACHE)


