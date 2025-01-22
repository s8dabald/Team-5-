import sqlite3


def execute_db_query(query, params=None):  #for editing/reading from the db
    db_name = "holzbau.db"
    try:
        with sqlite3.connect(db_name) as connection:
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            #checks which sql function is used
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP")):
                connection.commit()
                return cursor.rowcount
            else:

                return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"There was an error: {e}")
        return None

def delete_last_logged_mail(): #for testing purposes will be removed in final version I guess
    query = "DELETE FROM Email_Log WHERE rowid = (SELECT MAX(rowid) FROM Email_Log);"
    rows_affected = execute_db_query(query)
    if rows_affected:
        print(f"{rows_affected} Zeile(n) erfolgreich gelöscht.")
    else:
        print("Fehler beim Löschen der letzten Zeile.")
