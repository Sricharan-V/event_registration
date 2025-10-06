import sqlite3

def init_db():
    with open('schema.sql', 'r') as f:
        schema_sql = f.read()

    conn = sqlite3.connect('database.db')
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
