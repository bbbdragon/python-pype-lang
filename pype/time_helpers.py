import datetime as dt
from copy import deepcopy
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

BEGIN=dt.datetime(year=1970,month=1,day=1)
END=dt.datetime(year=2030,month=1,day=1)
DAY=dt.timedelta(days=1)

def date_range(begin,end):

    d=deepcopy(begin)
    rng=[d]

    while d < end:

        d+=DAY

        rng.append(d)

    return rng


def add_days(date,days=1):

    return date+dt.timedelta(days=int(days))


def add_months(date,months=1):

    return date+relativedelta(months=int(months))


def date_range_days(begin,days):

    return [begin+dt.timedelta(days=d) for d in range(days)]


def date_int_range_days(begin,days):

    return [date_int(d) for d in date_range_days(begin,days)]


def date_week_range(begin):

    return date_range_days(begin,7)


def date_string_week_range(begin):

    return [date_to_date_string(d) for d in date_range_days(begin,7)]


def date_string_range(beginDateString,endDateString):

    begin=parse(beginDateString)
    end=parse(endDateString)
    rng=date_range(begin,end)
    dateStrings=[date_string(d) for d in rng]

    return dateStrings

    
def date_int(date):

    return int(f'{date.year}'+'{0:0=2d}'.format(date.month)+'{0:0=2d}'.format(date.day))


def date_string(date):
    
    return date.strftime("%Y-%m-%d")


def begin_next_week(date):

    weekday=date.weekday()
    offset=7-weekday
    newDate=date+dt.timedelta(days=offset)

    return newDate


def begin_this_week(date):

    weekday=date.weekday()
    newDate=date-dt.timedelta(days=weekday)

    return newDate


def begin_this_week_string(dateString):

    return date_string(begin_this_week(parse(dateString)))


def begin_next_week_string(dateString):

    return date_string(begin_next_week(parse(dateString)))


def today():

    return datetime_to_date(dt.datetime.now())

def today_string():

    return date_string(today())


def date_to_month(date):

    return dt.datetime(year=date.year,month=date.month,day=1)


def datetime_to_date(date):

    return dt.datetime(year=date.year,month=date.month,day=date.day)



DATE_RANGE=date_range(BEGIN,END)
DATE_STRING_RANGE=[]
DATE_TO_INT_CACHE={}
INT_TO_DATE_CACHE={}
DATE_TO_STRING_CACHE={}
DATE_TO_WEEKDAY_CACHE={}
DATE_STRING_TO_DATE_CACHE={}
DATE_STRING_TO_NEXT_DATE_STRING_CACHE={}

for date in DATE_RANGE:

    dateString=date_string(date)
    dateInt=date_int(date)

    DATE_STRING_RANGE.append(dateString)

    DATE_TO_INT_CACHE[dateString]=dateInt
    DATE_TO_WEEKDAY_CACHE[dateString]=date.weekday()
    INT_TO_DATE_CACHE[dateInt]=dateString
    DATE_TO_STRING_CACHE[date]=dateString
    DATE_STRING_TO_DATE_CACHE[dateString]=date


for (date1,date2) in zip(DATE_STRING_RANGE,DATE_STRING_RANGE[1:]):

    DATE_STRING_TO_NEXT_DATE_STRING_CACHE[date1]=date2


from functools import reduce

def append_last_from_cache(ls,cache):

    el=ls[-1]
    newEl=cache[el]

    ls.append(newEl)

    return ls

def date_string_range_days(beginDateString,numDays):

    return reduce(lambda ls,x: append_last_from_cache(ls,
                                                      DATE_STRING_TO_NEXT_DATE_STRING_CACHE),
                  range(numDays),
                  [beginDateString])


def from_cache(x,cache):

    return cache[x]


def date_string_to_date(dateString):

    return from_cache(dateString,DATE_STRING_TO_DATE_CACHE)


def date_string_to_int(dateString):

    return from_cache(dateString,DATE_TO_INT_CACHE)


def date_to_date_string(date):

    return from_cache(date,DATE_TO_STRING_CACHE)


def int_to_date_string(dateInt):

    return from_cache(dateInt,INT_TO_DATE_CACHE)


def date_string_to_weekday_int(dateString):

    return from_cache(dateString,DATE_TO_WEEKDAY_CACHE)


def date_string_to_month_day_int(dateString):

    return int(dateString[-2:])


def date_string_to_bi_weekday_int(dateString):

    dayInt=date_string_to_month_day_int(dateString)

    if dayInt < 14:

        return dayInt

    return dayInt-14


def date_string_to_weekend_weekday_int(dateString):

    wd=date_string_to_weekday_int(dateString)

    return 0 if wd < 5 and wd >= 0 else 1


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


WEEKDAYS=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

def weekday_int_to_string(i):

    return WEEKDAYS[i]

def date_string_to_weekday_string(dateString):

    return weekday_int_to_string(date_string_to_weekday_int(dateString))


def today_date_string():

    return date_string(dt.datetime.now())


def increment_weekday(weekdayInt):

    return (weekdayInt + 1) % 7


def increment_date(date,days=1):

    return date+dt.timedelta(days=int(days))

def increment_date_string(dateString,days=1):

    return date_string(parse(dateString)+dt.timedelta(days=int(days)))


def tomorrow():

    return increment_date_string(today())


def weekday_interval_date_strings(weekBeginDateString,interval):

    beginDate=increment_date_string(weekBeginDateString,interval[0])
    endDate=increment_date_string(weekBeginDateString,interval[1])

    return date_string_range(beginDate,endDate)
