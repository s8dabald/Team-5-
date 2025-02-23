from datetime import datetime, date, timedelta
import asyncio
from dateutil import easter
from pandas import date_range
from database_manager import execute_db_query

settings_changed_event = asyncio.Event()#event that is triggered if someone changes the settings

def get_black_friday(year): #gets the black friday of the year -> 4th friday in november
    first_november = date(year, 11, 1).weekday() #find day of the week  of the first
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

def mail_logger(holiday, year):
    execute_db_query("INSERT INTO Email_Log (Holiday, Year) VALUES (?, ?);", (holiday, year))


def get_holiday_settings():
    query="SELECT * FROM Offers"
    settings = execute_db_query(query)
    return settings

def get_percentage():
    settings = get_holiday_settings()
    percentages = []
    percentages.append(settings[2][2])
    percentages.append(settings[1][2])
    percentages.append(settings[0][2])
    return percentages

def find_holidays():
    settings = get_holiday_settings()
    year = date.today().year  # Get the year
    holidays =  []
    #for each  of the holidays it checks if the offer is on and only includes them if it is 1-> on
    if settings[2][1]==1:
        holidays.append(["easter month", date(year, 4, 1)])
        holidays.append(["easter", easter.easter(year)])
    if settings[1][1]==1:
        holidays.append(["black month", date(year, 11, 1)])
        holidays.append(["black friday", get_black_friday(year)])
    if settings[0][1]==1:
        holidays.append(["1st of advent", date(year, 12, 1)])
        holidays.append(["christmas", date(year, 12, 24)])
    return holidays

def send_mail(holiday, year):
    if holiday:
        data = get_mail()
        mail_logger(holiday, year)
        year = str(year)[2:]
        percent = get_percentage()
        messages = {
            "1st of advent": "Hello {name},\nThank you for being a loyal customer of Holzbau GmbH! As a reward, you will receive {percent[2]}% off for your next purchase by using the code Christmas{year} at checkout! Only until December 24.\n\nBest regards,\nHolzbau GmbH\n",
            "christmas": "Hello {name},\nThank you for being a loyal customer of Holzbau GmbH! This is a reminder that today is your last chance to use the code Christmas{year} at checkout for {percent[2]}% off.\n\nBest regards and Merry Christmas,\nHolzbau GmbH\n",
            "black month": "Hello {name},\nThank you for being a loyal customer of Holzbau GmbH! As a reward, you will receive {percent[1]}% off for your next purchase by using the code BlackFriday{year} at checkout! Only until Black Friday.\n\nBest regards,\nHolzbau GmbH\n",
            "black friday": "Hello {name},\nThank you for being a loyal customer of Holzbau GmbH! This is a reminder that today is your last chance to use the code BlackFriday{year} at checkout for {percent[1]}% off.\n\nBest regards,\nHolzbau GmbH\n",
            "easter month": "Hello {name},\nThank you for being a loyal customer of Holzbau GmbH! As a reward, you will receive {percent[0]}% off for your next purchase by using the code Easter{year} at checkout! Only until Easter Sunday.\n\nBest regards,\nHolzbau GmbH\n",
            "easter": "Hello {name},\nThank you for being a loyal customer of Holzbau GmbH! This is a reminder that today is your last chance to use the code Easter{year} at checkout for {percent[0]}% off.\n\nBest regards and Happy Easter,\nHolzbau GmbH\n"
        }
        for email, name in data:
            print(f"send to: {email}\n{messages[holiday].format(name=name, year=year, percent = percent)}")

async def find_next_holiday(day):
    while True:
        try:
            await asyncio.wait_for(settings_changed_event.wait(), timeout=24 * 3600) #wait for 1 day or until settings are changed
        except asyncio.TimeoutError:
            pass
        today = day.date() #date.today()  # Get today's date only once per loop
        holidays = find_holidays()
        for holiday_name, holiday_date in holidays:

            if today == holiday_date:
                send_mail(holiday_name, today.year)  # Pass holiday name and year
                break  # Exit the inner loop after sending the mail for the current holiday
        print("sleep")


def check_log_for_mail(holiday, year):
    last_holiday = execute_db_query("SELECT Holiday FROM Email_Log ORDER BY id DESC LIMIT 1")[0][0]
    last_year = execute_db_query("SELECT Year FROM Email_Log ORDER BY id DESC LIMIT 1")[0][0]
    #as both of these return a list of tuples [0][0] is used to return the desired element
    if last_holiday == holiday and last_year==year:
        return True
    else:
        return False

async def find_last_holiday(day):
    recent_month = date_range(start=day, end=day - timedelta(days=30), freq="-1D")
    print(recent_month)
    #recent_month = date_range(start=date.today(), end=date.today() - timedelta(days=30), freq="-1D")
    holidays = find_holidays()
    for x in recent_month:
        for holiday_name, holiday_date in holidays:
            if x.date() == holiday_date:
                if holiday_name in ["1st of advent", "easter month", "black month"]:
                    if not check_log_for_mail(holiday_name, x.year): #bcs it returns True if it finds a match
                        send_mail(holiday_name, x.year)
                await find_next_holiday(day)
                return #if it ever finds one of the holiday dates then there is no point to continue past that point
    await find_next_holiday(day) #if we dont find a holiday we still wanna continue to the next part.

#testing
send_mail("1st of advent", 2025)
#check_log_for_mail("christmas",2020)
#get_holiday_settings()
"""
async def main():
    offers_task = asyncio.create_task(find_last_holiday(datetime(2025,12,24)))
    await asyncio.gather(offers_task)

asyncio.run(main())
"""