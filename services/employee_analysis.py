import pandas as pd
from database_manager import execute_db_query


def get_employee_data():
    """
    This function fetches employee data from the Employee_DB table in the database.
    It executes the SQL query to retrieve all records and loads the result into a DataFrame.
    If no data is retrieved, it returns an empty DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing all employee data, or an empty DataFrame if no data exists.
    """
    # Execute the SQL query to select all data from Employee_DB table
    employee_data = execute_db_query("SELECT * FROM Employee_DB", as_dict=True)

    # Check if the query returned any results. If there is data, create a DataFrame from it.
    # If the data is empty, return an empty DataFrame.
    employees = pd.DataFrame([dict(row) for row in employee_data]) if employee_data else pd.DataFrame()

    # Return the DataFrame containing the employee data
    return employees


def get_employee_distributions():
    """
    This function retrieves the employee data using the get_employee_data function,
    and calculates the distribution of employees based on two categories:
    - The country distribution (how many employees per country)
    - The job distribution (how many employees per job ID)

    Returns:
        tuple: A tuple containing two dictionaries:
            - The first dictionary: Country distribution (key: country, value: employee count)
            - The second dictionary: Job ID distribution (key: job ID, value: employee count)
    """
    # Retrieve employee data by calling the get_employee_data function
    employees = get_employee_data()

    # Calculate the distribution of employees by country using value_counts (counts occurrences of each value)
    # Convert the result into a dictionary where the keys are the countries and the values are the counts
    employee_country_distrbution = employees['Country'].value_counts().to_dict()

    # Similarly, calculate the distribution of employees by JobId using value_counts
    # Convert the result into a dictionary where the keys are the JobIds and the values are the counts
    employee_job_distribution = employees['JobId'].value_counts().to_dict()

    # Return the two distributions as a tuple (Country distribution, Job distribution)
    return employee_country_distrbution, employee_job_distribution
