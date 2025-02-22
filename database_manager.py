import sqlite3

def execute_db_query(query, params=None):  # Function for reading/writing to the DB
    db_name = "holzbau.db"  # Make sure this path is correct
    try:
        with sqlite3.connect(db_name) as connection:

            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)  # Execute query with parameters if provided
            else:
                cursor.execute(query)  # Execute query without parameters

            # Check for modifying queries (INSERT, UPDATE, DELETE, etc.)
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP")):
                connection.commit()  # Commit changes for modifying queries
                return cursor.rowcount  # Return number of affected rows
            else:
                return cursor.fetchall()  # Return fetched results for SELECT queries
    except sqlite3.Error as e:
        print(f"There was an error: {e}")  # Print the error
        return None  # Return None in case of error

# Testing function (can be removed later)
def delete_last_logged_mail():
    query = "DELETE FROM Email_Log WHERE rowid = (SELECT MAX(rowid) FROM Email_Log);"
    rows_affected = execute_db_query(query)
    if rows_affected:
        print(f"{rows_affected} row(s) successfully deleted.")
    else:
        print("Error deleting the last row.")


