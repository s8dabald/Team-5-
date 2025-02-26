from datetime import datetime, date, timedelta
import time
from dateutil import easter
from pandas import date_range
from database_manager import execute_db_query

# Function to get the date of Black Friday for a given year
def get_black_friday(year):
    """
    Calculate the date of Black Friday in November for a given year.
    Black Friday is the fourth Friday of November.

    Args:
        year (int): The year for which to calculate Black Friday.

    Returns:
        datetime.date: The date of Black Friday.
    """
    first_november = date(year, 11, 1).weekday()  # Get the weekday of November 1st
    # Calculate the 4th Friday of November
    if first_november <= 4:
        black_friday = 22 + (4 - first_november)
    else:
        black_friday = 29 - (first_november - 4)
    return datetime(year, 11, black_friday).date()

# Function to retrieve customer emails and names from the database
def get_mail():
    """
    Retrieves customer emails and names from the database.

    Returns:
        list: A list of tuples with email and name for each customer.
    """
    data = []
    try:
        # Fetch customer emails and names from the database
        emails = execute_db_query("SELECT Email FROM Customer_DB")
        names = execute_db_query("SELECT Name FROM Customer_DB")
        # Combine emails and names into a list of tuples
        for email, name in zip(emails, names):
            data.append([email[0], name[0]])
    except Exception as e:
        # Log any error during database query
        print(f"Error fetching mail data: {e}")
    return data

# Function to log sent mail for a holiday and year
def mail_logger(holiday, year):
    """
    Logs the sent email information to the database.

    Args:
        holiday (str): The holiday name for the email.
        year (int): The year of the holiday.
    """
    try:
        # Insert mail log into the database
        execute_db_query("INSERT INTO Email_Log (Holiday, Year) VALUES (?, ?);", (holiday, year))
    except Exception as e:
        # Log any error during database operation
        print(f"Error logging email: {e}")

# Function to get holiday settings from the database
def get_holiday_settings():
    """
    Retrieves the holiday settings from the database.

    Returns:
        list: A list of tuples representing holiday settings.
    """
    query = "SELECT * FROM Offers"
    try:
        settings = execute_db_query(query)
    except Exception as e:
        print(f"Error fetching holiday settings: {e}")
        settings = []
    return settings

# Function to get percentage discounts based on the holiday settings
def get_percentage():
    """
    Retrieves percentage discounts for the holidays.

    Returns:
        list: A list of percentage discounts for each holiday.
    """
    settings = get_holiday_settings()
    percentages = []
    try:
        # Extract percentage values from the settings
        percentages.append(settings[2][2])
        percentages.append(settings[1][2])
        percentages.append(settings[0][2])
    except IndexError:
        print("Error: Holiday settings do not have the expected structure.")
    return percentages

# Function to find upcoming holidays based on the current settings
def find_holidays():
    """
    Finds upcoming holidays based on the current holiday settings.

    Returns:
        list: A list of tuples with holiday names and their respective dates.
    """
    settings = get_holiday_settings()
    year = date.today().year  # Get the current year
    holidays = []
    try:
        # Check which holidays are enabled and add them to the list
        if settings[2][1] == 1:
            holidays.append(["easter month", date(year, 4, 1)])
            holidays.append(["easter", easter.easter(year)])
        if settings[1][1] == 1:
            holidays.append(["black month", date(year, 11, 1)])
            holidays.append(["black friday", get_black_friday(year)])
        if settings[0][1] == 1:
            holidays.append(["1st of advent", date(year, 12, 1)])
            holidays.append(["christmas", date(year, 12, 24)])
    except IndexError:
        print("Error: Holiday settings structure is incorrect.")
    return holidays

# Function to send an email with the discount code for a specific holiday
def send_mail(holiday, year):
    """
    Sends an email to customers with a discount code for a specific holiday.

    Args:
        holiday (str): The name of the holiday.
        year (int): The year of the holiday.
    """
    if holiday:
        data = get_mail()
        mail_logger(holiday, year)
        year = str(year)[2:]  # Get last two digits of the year for the code
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
            print(f"send to: {email}\n{messages[holiday].format(name=name, year=year, percent=percent)}")

# Function to check if an email has already been sent for a specific holiday and year
def check_log_for_mail(holiday, year):
    """
    Checks the email log to see if an email has already been sent for a specific holiday and year.

    Args:
        holiday (str): The holiday name.
        year (int): The year of the holiday.

    Returns:
        bool: True if the email has already been sent, False otherwise.
    """
    try:
        last_holiday = execute_db_query("SELECT Holiday FROM Email_Log ORDER BY id DESC LIMIT 1")[0][0]
        last_year = execute_db_query("SELECT Year FROM Email_Log ORDER BY id DESC LIMIT 1")[0][0]
        return last_holiday == holiday and last_year == year
    except Exception as e:
        print(f"Error checking email log: {e}")
        return False

# Function to find the next holiday and send emails accordingly
def find_next_holiday():
    """
    Periodically checks for the next holiday and sends emails to customers.
    """
    print("Checking for recent special days completed.")
    while True:
        time.sleep(24 * 3600)  # Always wait for 24 hours
        print("Checking if today is a special day.")
        today = date.today()  # Update to current date inside the loop
        holidays = find_holidays()  # Retrieve the list of holidays

        # Check if today matches any holiday date
        for holiday_name, holiday_date in holidays:
            if today == holiday_date:
                send_mail(holiday_name, today.year)  # Send email for the holiday
                break  # Exit the loop after sending the mail for the current holiday



# Function to check the log and send mail if necessary for holidays in the last 30 days
def find_last_holiday():
    """
    Checks if any holiday from the last 30 days has not been logged, then sends the email.
    """
    print("Checking recent month for special days")  # Debug print statement

    while True:
        recent_month = date_range(start=date.today(), end=date.today() - timedelta(days=30), freq="-1D")  # Get last 30 days
        holidays = find_holidays()  # Get the holidays for the year

        # Iterate through the recent month and check for holidays
        for x in recent_month:
            for holiday_name, holiday_date in holidays:
                if x.date() == holiday_date:
                    if holiday_name in ["1st of advent", "easter month", "black month"]:
                        if not check_log_for_mail(holiday_name, x.year):
                            send_mail(holiday_name, x.year)
                    find_next_holiday()  # Proceed to find the next holiday
                    return  # No need to continue past this point if a holiday is found
        find_next_holiday()  # Continue to check for future holidays
