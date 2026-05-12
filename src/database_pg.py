import psycopg2
import os

GM_AP_POOL_MAX = 25
PLAYER_AP_POOL_MAX = 5
PLAYER_AP_POOL = "player_group"
GM_AP_POOL = "gm"


def get_connection():
    db_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(db_url)

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

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


def add_ap(pool_name: str, amount: int) -> int:
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


def spend_ap(pool_name: str, amount: int) -> int:
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
