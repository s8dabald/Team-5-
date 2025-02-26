import pandas as pd
from database_manager import execute_db_query

def get_employee_data():#to get data from DB
    employee_data = execute_db_query("SELECT * FROM Employee_DB", as_dict=True)
    #after the db execute puts  it in a dataframe if the data is empty creates  an empty dataframe
    employees = pd.DataFrame([dict(row) for row in employee_data]) if employee_data else pd.DataFrame()
    return employees

def get_employee_distributions():#gets the different segments
    employees = get_employee_data()
    employee_country_distrbution = employees['Country'].value_counts().to_dict()
    employee_job_distribution = employees['JobId'].value_counts().to_dict()
    return employee_country_distrbution, employee_job_distribution
