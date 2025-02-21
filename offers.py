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
    if first_november <= 4:  # Monday-Friday
        black_friday = 22 + (4 - first_november)
    else:  # Saturday-Sunday
        black_friday = 29 - (first_november - 4)
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
def holiday_check(heute):
    year = heute.year
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
"""for each of the 3 holidays that are supposed to have a special offer this checks if it's the day off the holiday
of the first of the month of said holiday.
"""

def mail_logger(holiday, year): #logs the sent mails
    execute_db_query("INSERT INTO Email_Log (Holiday, Year) VALUES (?, ?);", (holiday, year))
"""saves  the  date and which holiday to the table Email_Log on the database"""

def send_mail(holiday, year):
    if holiday != None: #if there is no holiday there is no reason to send the mail
            data = get_mail() #retrieves the name and email
            mail_logger(holiday, year) #logs the mail
            year = str(year)[2:] #to "generate" the code being sent
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
"""this function is called upon when a holiday has been found and is given the holiday and the year and simply sends (prints) the mail
"""
def find_next_holiday():
    while  True: #this is supposed to run permanently to always check for the next holiday
        holidays = [
            ["Easter Month", datetime(date.today().year, 4, 1).date()],
            ["Easter", easter.easter(date.today().year)],
            ["Black Month", datetime(date.today().year, 11, 1).date()],
            ["Black Friday", get_black_friday(date.today().year)],
            ["1st of Advent", datetime(date.today().year, 12, 1).date()],
            ["Christmas", datetime(date.today().year, 12, 25).date()]]
        #just a list of all holidays and their dates
        i= 0
        while i < len(holidays):
            check =  holidays[i][1]-datetime.today().date() #checks how long until next holiday
            if check >= timedelta(0): #if this is 0 or positive it means there is a holiday today or in the future
                time.sleep(check.total_seconds()) #waits for the  day of  the holiday
                send_mail(holidays[i][0], date.today().year) #sends the mail

            i+=1
        time.sleep(timedelta(days=30).total_seconds())
"""This function finds the next holiday. As the list of holidays is in order it can just run through all of them
in the inner while loop. As it reaches the end of said loop after Christmas but simply restarting  the whole permanent 
while loop would yield a check  that is always < 0 as the all the holidays of this year would be over it waits for
30 days after christmas to arrive at the next year and thus start again at Easter Month."""

def check_log_for_mail(holiday, year):
    if holiday == execute_db_query("SELECT Holiday FROM Email_Log ORDER BY id DESC LIMIT 1") and year == execute_db_query("SELECT Year FROM Email_Log ORDER BY id DESC LIMIT 1"):
        return(True)
    else:
        return(False)
"""just checks if the last entry in the Email_Log is the holiday found by find_last_holiday thus confirming that
the last holiday mail has been sent."""

def find_last_holiday(): #checks to see if there should have been a mail sent within the last 30 days
    recent_month = date_range(start =date.today(), end = date.today()+timedelta(-30),freq ="-1D")
    for x in recent_month:
        holiday = holiday_check(x.date())
        if holiday in ["1st of Advent", "Easter Month", "Black Month"]:  # Only check for start-of-month holidays
            if check_log_for_mail(holiday, x.year) == False:
                send_mail(holiday, x.year)
    find_next_holiday()
"""if the holiday itself has already happened there is no reason to send a mail as the time period of the offer has already ended
thus it only sends a mail if the period has started but the holiday itself has not happened yet so when it finds that a holiday
itself has happened within the last 30 days holiday_check will not return None, the if statement becomes true but the second
if becomes false thus simply returning None
"""


#find_last_holiday() to start
