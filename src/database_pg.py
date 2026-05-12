import psycopg2
import os

GM_AP_POOL_MAX = 25
PLAYER_AP_POOL_MAX = 5
PLAYER_AP_POOL = "player_group"
GM_AP_POOL = "gm"


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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS action_point_pools (
        pool_name TEXT PRIMARY KEY,
        current_ap INTEGER NOT NULL DEFAULT 0,
        max_ap INTEGER NOT NULL DEFAULT 25
    )
    ''')

    cursor.execute('''
        INSERT INTO action_point_pools (pool_name, current_ap, max_ap)
        VALUES (%s, 0, %s)
        ON CONFLICT (pool_name)
        DO UPDATE SET
            max_ap = EXCLUDED.max_ap,
            current_ap = LEAST(action_point_pools.current_ap, EXCLUDED.max_ap)
    ''', (PLAYER_AP_POOL, PLAYER_AP_POOL_MAX))

    cursor.execute('''
        INSERT INTO action_point_pools (pool_name, current_ap, max_ap)
        VALUES (%s, 0, %s)
        ON CONFLICT (pool_name)
        DO UPDATE SET
            max_ap = EXCLUDED.max_ap,
            current_ap = LEAST(action_point_pools.current_ap, EXCLUDED.max_ap)
    ''', (GM_AP_POOL, GM_AP_POOL_MAX))
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


def get_ap(pool_name: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT current_ap FROM action_point_pools WHERE pool_name = %s', (pool_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return 0


def add_ap_clamped(pool_name: str, amount: int) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE action_point_pools
        SET current_ap = LEAST(current_ap + %s, max_ap)
        WHERE pool_name = %s
        RETURNING current_ap
    ''', (amount, pool_name))
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    if result:
        return result[0]
    return 0


def spend_ap_clamped(pool_name: str, amount: int) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE action_point_pools
        SET current_ap = GREATEST(current_ap - %s, 0)
        WHERE pool_name = %s
        RETURNING current_ap
    ''', (amount, pool_name))
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    if result:
        return result[0]
    return 0
