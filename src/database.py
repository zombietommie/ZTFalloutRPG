import sqlite3

def setup_database():
    conn = sqlite3.connect('fallout.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
    user_id INTEGER PRIMARY KEY,
    character_name TEXT,
    cap INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
    conn.close()

def get_player_caps(user_id):
    conn = sqlite3.connect('fallout.db')
    cursor = conn.cursor()

    cursor.execute('SELECT cap FROM players WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    return 0