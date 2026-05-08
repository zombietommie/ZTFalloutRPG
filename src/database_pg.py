import psycopg2
import os


def get_connection():
    # We will get the connection URL from the environment variables
    # The cloud provider will give you a URL like: postgresql://user:password@host:port/dbname
    db_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(db_url)

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    # PostgreSQL uses SERIAL for auto-incrementing integers or BIGINT for Discord IDs
    # and ON CONFLICT instead of INSERT OR IGNORE

    # This is to create a new table if it doesn't exist already.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        user_id BIGINT PRIMARY KEY,
        character_name TEXT,
        cap INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
    conn.close()

def get_player_caps(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Note the change: PostgreSQL uses %s for variables, not ?
    cursor.execute('SELECT cap FROM players WHERE user_id = %s', (user_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    return 0

def insert_player(user_id, character_name, caps=0):
    conn = get_connection()
    cursor = conn.cursor()

    # PostgreSQL handles existing entries with ON CONFLICT DO NOTHING
    cursor.execute('''
        INSERT INTO players (user_id, character_name, cap)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    ''', (user_id, character_name, caps))

    conn.commit()
    conn.close()

def award_caps(user_id, caps):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE players
        SET cap = cap + %s 
        WHERE user_id = %s
    ''', (caps, user_id))
    conn.commit()
    conn.close()

def remove_caps_clamped(user_id: int, amount: int) -> int:
    """Remove caps from a user, clamping the result to a minimum of 0.
    
    This function performs an atomic UPDATE operation that subtracts the specified
    amount from the user's cap balance, ensuring the result never goes below 0.
    
    :param user_id: The Discord user ID
    :param amount: Number of caps to remove
    :return: The new cap value after removal
    
    Note: This assumes the user exists in the database. The caller should ensure
    the user is inserted via insert_player() before calling this function.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE players
            SET cap = GREATEST(cap - %s, 0)
            WHERE user_id = %s
            RETURNING cap
        ''', (amount, user_id))
        result = cursor.fetchone()
        conn.commit()
        
        if result:
            return result[0]
        # Return 0 if user doesn't exist (shouldn't happen if insert_player was called first)
        return 0
    finally:
        conn.close()


def set_player_caps(user_id, cap):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE players
        SET cap = %s
        WHERE user_id = %s
    ''', (cap, user_id))
    conn.commit()
    conn.close()