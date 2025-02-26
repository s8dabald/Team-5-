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


