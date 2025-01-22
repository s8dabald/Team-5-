from datetime import datetime
from datetime import date
from datetime import timedelta
import time

from dateutil import easter
from pandas import date_range

from database_manager import execute_db_query

def get_black_friday(year): #gets black friday of the current year -> 4th  friday in november
    first_november = date(year,11,1).weekday() #weekday of 01/11
    black_friday = 1
    black_friday_string =  ""
    if first_november <= 4: #if 01/11  is Mo-Fr
        black_friday += (4-first_november) + 21
    else: #if 01/11 is Sa/Su
        black_friday += (4 - first_november) + 28
    return(datetime(year,11,black_friday).date())

def get_mail(): #gets the email and first name of all customers and returns it as a list of lists where 0 is the email and 1 is the name
    data = []
    emails =  execute_db_query("SELECT Email FROM Customer_DB")
    names = execute_db_query("SELECT Name FROM Customer_DB")
    i=0
    while i < len(emails):
        data.append([emails[i][0],names[i][0]])
        i+=1
    return(data)

def holiday_check(heute:datetime.date):
    year = heute.year()
    if heute == datetime(year,12,24).date():
        return("Christmas")
    elif heute == datetime(year,12,1).date():
        return("1st of advent")
    elif heute == datetime(year,11,1).date():
        return("black month")
    elif heute == get_black_friday(year):
        return("black friday")
    elif heute == datetime(year,4,1).date():
        return ("easter month")
    elif heute == easter.easter(year):
        return("easter")

def mail_logger(holiday, year): #logs the sent mails
    execute_db_query("INSERT INTO Email_Log (Holiday, Year) VALUES (?, ?);", (holiday, year))

def send_mail(holiday, year):

    if holiday != None:
            data = get_mail() #retrieves the name and email
            mail_logger(holiday, year)
            year = str(year)[2:]
            if holiday == "1st of advent":
                for x in data:
                    print("send to:",x[0],"\nHello",x[1]+",","\nthank you for being a loyal customer of Holzbau GmbH!\nas a reward you will receive 5% off for your next purchase "
                                                            "by using the code Christmas"+year,"at checkout! Only until December 24.\n\nbest regards\nHolzbau GmbH\n")
            elif holiday == "Christmas":
                for x in data:
                    print("send to:",x[0],"\nHello",x[1]+",","\nthank you for being a loyal customer of Holzbau GmbH!\nthis is a reminder that today is your last chance "
                                                              "to use the code Christmas"+year," at checkout for 5% off.\n\nbest regards and merry Christmas\nHolzbau GmbH\n")
            elif holiday == "black month":
                for x in data:
                    print("send to:",x[0],"\nHello",x[1]+",","\nthank you for being a loyal customer of Holzbau GmbH!\nas a reward you will receive 5% off for your next purchase "
                                                            "by using the code BlackFriday"+year ,"at checkout! Only until black friday.\n\nbest regards\nHolzbau GmbH\n")
            elif holiday == "black friday":
                for x in data:
                    print("send to:",x[0],"\nHello",x[1]+",","\nthank you for being a loyal customer of Holzbau GmbH!\nthis is a reminder that today is your last chance "
                                                              "to use the code BlackFriday"+year ,"at checkout for 5% off.\n\nbest regards\nHolzbau GmbH\n")
            elif holiday == "easter month":
                for x in data:
                    print("send to:",x[0],"\nHello",x[1]+",","\nthank you for being a loyal customer of Holzbau GmbH!\nas a reward you will receive 5% off for your next purchase "
                                                            "by using the code Easter"+year ,"at checkout! Only until easter sunday.\n\nbest regards\nHolzbau GmbH\n")
            elif holiday == "easter":
                for x in data:
                    print("send to:",x[0],"\nHello",x[1]+",","\nthank you for being a loyal customer of Holzbau GmbH!\nthis is a reminder that today is your last chance "
                                                              "to use the code Easter"+year ,"at checkout for 5% off.\n\nbest regards and happy easter\nHolzbau GmbH\n")
def find_next_holiday():
    while  True:
        holidays = [
            ["Easter Month", datetime(date.today().year, 4, 1).date()],
            ["Easter", easter.easter(date.today().year)],
            ["Black Month", datetime(date.today().year, 11, 1).date()],
            ["Black Friday", get_black_friday(date.today().year)],
            ["1st of Advent", datetime(date.today().year, 12, 1).date()],
            ["Christmas", datetime(date.today().year, 12, 25).date()]]
        i= 0
        while i < len(holidays):
            check =  holidays[i][1]-datetime.today().date()
            if check >= timedelta(0):
                time.sleep(check.total_seconds())
                send_mail(holidays[i][0], date.today().year)
                find_next_holiday()
            i+=1
        time.sleep(timedelta(days=30).total_seconds())


def check_log_for_mail(holiday, year):
    if holiday == execute_db_query("SELECT Holiday FROM Email_Log ORDER BY id DESC LIMIT 1") and year == execute_db_query("SELECT Year FROM Email_Log ORDER BY id DESC LIMIT 1"):
        return(True)
    else:
        return(False)

def find_last_holiday(): #checks to see if there should have been a mail sent within the last 30 days
    recent_month = date_range(start =date.today(), end = date.today()+timedelta(-30),freq ="-1D")
    for x  in  recent_month:
        if holiday_check(x) != None:
            if holiday_check(x) == "1st of advent" or "easter month" or "black month":
                if  check_log_for_mail(holiday_check(x), x.year()) == False:
                    send_mail(holiday_check(x), x.year())
                return(None)
            else:
                return(None)
"""if the holiday itself has already happened there is no reason to send a mail as the time period of the offer has already ended
thus it only sends a mail if the period has started but the holiday itself has not happened yet so when it finds that a holiday
itself has happened within the last 30 days holiday_check will not return None, the if statement becomes true but the second
if becomes false thus simply returning None
"""


find_next_holiday()