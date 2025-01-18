from datetime import date
from dateutil import easter
import main
from database_manager import get_from_db


def todays_date():#gets todays date and cuts off the year to return a string
    heute = str(date.today())[5:]
    return(heute)

def get_black_friday(): #gets black friday of the current year -> 4th  friday in november
    year = date.today().year
    first_november = date(year,11,1).weekday() #weekday of 01/11
    black_friday = 1
    black_friday_string =  ""
    if first_november <= 4: #if 01/11  is Mo-Fr
        black_friday += (4-first_november) + 21
    else: #if 01/11 is Sa/Su
        black_friday += (4 - first_november) + 28
    black_friday_string = "11-"+ str(black_friday)
    return(black_friday_string)

def get_easter():
    year = date.today().year
    return(easter.easter(year)[5:])

def send_mail():
    emails =  get_from_db("SELECT Email FROM Customer_DB")

    for x in emails:
        print(x[0])
def holiday_check():
    heute = todays_date()
    if heute == "12-24":
        return("Christmas")
    elif heute == "12-01":
        return("1st of advent")
    elif heute == "11-01":
        return("black month")
    elif heute == get_black_friday():
        return("black friday")
    elif heute == "04-01":
        return ("easter month")
    elif heute == get_easter():
        print("banana")



print(send_mail())


