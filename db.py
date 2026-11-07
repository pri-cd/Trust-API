# database.py
import sqlite3
import os

DB_NAME = "trustscore.db"

def get_db_connection():
    """ 
    > Connects to the SQLite file. If it doesn't exist, it creates it. 
    > Row Factory enabling, refer: https://www.pythonlore.com/using-sqlite3-row-factory-for-custom-row-objects/
    > Enables dict like access..
    """ 
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    """Creates the events table if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Basic SQL: CREATE TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            ip_address TEXT,
            timestamp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_event(event_data: dict) -> int:
    """Inserts a new event into the database and returns its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    """
        > Using parametrized queries..
        > Also, using ".get()" method for [optional fields] since they return None as default.
    """
    cursor.execute('''
        INSERT INTO events (device_id, user_id, session_id, event_type, ip_address, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        event_data['device_id'],
        event_data['user_id'],
        event_data['session_id'],
        event_data['event_type'],
        event_data.get('ip_address'),
        event_data.get('timestamp')
    ))
    
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    
    if event_id is None:
        raise RuntimeError("The inserted event ID was not generated.")
    
    return event_id


def is_new_device(device_id : str) -> bool:
    """ 
    > Check if device ID already exists in the DB, 
    > If device is new, return "True".
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM events WHERE device_id = ?', (device_id,))
    count = cursor.fetchone()[0]
    cursor.close()

    return (count == 0)