import sqlite3


def execute_db_query(query, params=None, as_dict=False):
    """
    Executes a database query and handles connections properly.

    - query: The SQL query to execute.
    - params: Optional parameters for parameterized queries.
    - as_dict: If True, returns results as a list of dictionaries.

    Returns fetched results for SELECT queries, or affected row count for modifying queries.
    """
    db_name = "holzbau.db"  # Database file
    try:
        # Open connection
        connection = sqlite3.connect(db_name)

        # If as_dict is enabled, return results as dictionary-like objects
        if as_dict:
            connection.row_factory = sqlite3.Row

        with connection:  # Ensures commit & proper closing
            cursor = connection.cursor()

            # Execute query with or without parameters
            cursor.execute(query, params or ())

            # If it's a modifying query, commit the changes
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP")):
                connection.commit()
                return cursor.rowcount  # Return number of affected rows

            # Otherwise, return the fetched results
            return cursor.fetchall()

    except sqlite3.Error as e:
        print(f"Database error: {e}")  # Print error for debugging
        return None  # Return None on failure

    finally:
        connection.close()  # Ensure the connection is always closed


def delete_last_logged_mail():
    """
    Deletes the most recently logged email from the Email_Log table.
    Ensures the table isn't empty before attempting the delete.
    """
    try:
        # First, check if there are any records
        check_query = "SELECT COUNT(*) FROM Email_Log;"
        result = execute_db_query(check_query)

        # If the table isn't empty, proceed with the delete
        if result and result[0][0] > 0:
            delete_query = "DELETE FROM Email_Log WHERE rowid = (SELECT MAX(rowid) FROM Email_Log);"
            rows_affected = execute_db_query(delete_query)

            if rows_affected:
                print(f"{rows_affected} row(s) successfully deleted.")
            else:
                print("Error deleting the last row.")
        else:
            print("No data to delete.")

    except Exception as e:
        print(f"Error in delete_last_logged_mail: {e}")
