import datetime, calendar


def months_to_days(add_months, date=datetime.date.today()):
    """
    Adds a number of months to a start year and month, and returns the number of days
    """

    days          = 0
    months_walked = 0
    
    year  = date.year
    month = date.month

    while months_walked < add_months:
        days += days_in_month(year, month)

        year, month = next_month(year, month)
        months_walked += 1

    return days


def next_month(year, month):
    date = datetime.date(year, month, 28)
    date + datetime.timedelta(days=4)
    return date.year, date.month
    

def days_in_month(year, month):
    return calendar.monthrange(year, month)[1]