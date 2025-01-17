import sqlite3

def get_from_db(query, params=None): #for database requests
    db_name = "holzbau.db"
    try:
        with sqlite3.connect(db_name) as connection:
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:

                cursor.execute(query)


            results = cursor.fetchall()
            return results
    except sqlite3.Error as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        return(None)