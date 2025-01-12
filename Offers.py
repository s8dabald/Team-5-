from datetime import date

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
def holiday_check():
    heute = todays_date()
    if heute == "12-24":
        return("Christmas")
    elif heute == "12-01":
        return("1st of advent")
    #elif heute == ""


print(get_black_friday())


