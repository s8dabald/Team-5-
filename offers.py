from datetime import datetime, date, timedelta
import asyncio
from dateutil import easter
from pandas import date_range
from database_manager import execute_db_query

def get_black_friday(year):
    first_november = date(year, 11, 1).weekday()
    black_friday = 1
    if first_november <= 4:
        black_friday = 22 + (4 - first_november)
    else:
        black_friday = 29 - (first_november - 4)
    return datetime(year, 11, black_friday).date()

def get_mail():
    data = []
    emails = execute_db_query("SELECT Email FROM Customer_DB")
    names = execute_db_query("SELECT Name FROM Customer_DB")
    for email, name in zip(emails, names):
        data.append([email[0], name[0]])
    return data

def holiday_check(today):
    year = today.year
    if today == datetime(year, 12, 24).date():
        return "Christmas"
    elif today == datetime(year, 12, 1).date():
        return "1st of advent"
    elif today == datetime(year, 11, 1).date():
        return "black month"
    elif today == get_black_friday(year):
        return "black friday"
    elif today == datetime(year, 4, 1).date():
        return "easter month"
    elif today == easter.easter(year):
        return "easter"
    return None

def mail_logger(holiday, year):
    execute_db_query("INSERT INTO Email_Log (Holiday, Year) VALUES (?, ?);", (holiday, year))

def send_mail(holiday, year):
    if holiday:
        data = get_mail()
        mail_logger(holiday, year)
        year = str(year)[2:]
        messages = {
            "1st of advent": "Hello {name},\nThank you for being a loyal customer of Holzbau GmbH! As a reward, you will receive 5% off for your next purchase by using the code Christmas{year} at checkout! Only until December 24.\n\nBest regards,\nHolzbau GmbH\n",
            "Christmas": "Hello {name},\nThank you for being a loyal customer of Holzbau GmbH! This is a reminder that today is your last chance to use the code Christmas{year} at checkout for 5% off.\n\nBest regards and Merry Christmas,\nHolzbau GmbH\n",
            "black month": "Hello {name},\nThank you for being a loyal customer of Holzbau GmbH! As a reward, you will receive 5% off for your next purchase by using the code BlackFriday{year} at checkout! Only until Black Friday.\n\nBest regards,\nHolzbau GmbH\n",
            "black friday": "Hello {name},\nThank you for being a loyal customer of Holzbau GmbH! This is a reminder that today is your last chance to use the code BlackFriday{year} at checkout for 5% off.\n\nBest regards,\nHolzbau GmbH\n",
            "easter month": "Hello {name},\nThank you for being a loyal customer of Holzbau GmbH! As a reward, you will receive 5% off for your next purchase by using the code Easter{year} at checkout! Only until Easter Sunday.\n\nBest regards,\nHolzbau GmbH\n",
            "easter": "Hello {name},\nThank you for being a loyal customer of Holzbau GmbH! This is a reminder that today is your last chance to use the code Easter{year} at checkout for 5% off.\n\nBest regards and Happy Easter,\nHolzbau GmbH\n"
        }
        for email, name in data:
            print(f"send to: {email}\n{messages[holiday].format(name=name, year=year)}")

async def find_next_holiday():
    while True:
        holidays = [
            ["Easter Month", datetime(date.today().year, 4, 1).date()],
            ["Easter", easter.easter(date.today().year)],
            ["Black Month", datetime(date.today().year, 11, 1).date()],
            ["Black Friday", get_black_friday(date.today().year)],
            ["1st of Advent", datetime(date.today().year, 12, 1).date()],
            ["Christmas", datetime(date.today().year, 12, 25).date()]
        ]
        for holiday, holiday_date in holidays:
            delta = (holiday_date - datetime.today().date()).days
            if delta >= 0:
                await asyncio.sleep(delta * 86400)  # Convert days to seconds
                send_mail(holiday, date.today().year)
        await asyncio.sleep(30 * 86400)  # Sleep for 30 days

def check_log_for_mail(holiday, year):
    last_holiday = execute_db_query("SELECT Holiday FROM Email_Log ORDER BY id DESC LIMIT 1")
    last_year = execute_db_query("SELECT Year FROM Email_Log ORDER BY id DESC LIMIT 1")
    return holiday == last_holiday and year == last_year

async def find_last_holiday():
    recent_month = date_range(start=date.today(), end=date.today() - timedelta(days=30), freq="-1D")
    for x in recent_month:
        holiday = holiday_check(x.date())
        if holiday in ["1st of Advent", "Easter Month", "Black Month"]:
            if not check_log_for_mail(holiday, x.year):
                send_mail(holiday, x.year)
    await find_next_holiday()