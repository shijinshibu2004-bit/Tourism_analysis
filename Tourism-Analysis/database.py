import sqlite3

def create_database():
    conn = sqlite3.connect("tourism.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS tourism_data (
                        id INTEGER PRIMARY KEY,
                        country TEXT,
                        visitors INTEGER,
                        year INTEGER,
                        season TEXT,
                        spending FLOAT)''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
