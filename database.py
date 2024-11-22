import mysql.connector
from config import DB_CONFIG, LOG_FILE
import logging

def connect_to_db():
    """Create a new database connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

def initialize_db():
    """Initialize the database schema."""
    conn = connect_to_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS power_status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cycle_id INT NOT NULL,
                timestamp DATETIME NOT NULL,
                device_id VARCHAR(255) NOT NULL,
                fog BOOLEAN NOT NULL,
                plasma BOOLEAN NOT NULL,
                pump BOOLEAN NOT NULL,
                description TEXT NOT NULL
            )
        """)
        conn.commit()
        logging.info("Database initialized successfully.")
    finally:
        conn.close()

def save_to_db(device_id, states, description, cycle_id):
    """Insert a new status record into the database."""
    conn = connect_to_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO power_status (cycle_id, timestamp, device_id, fog, plasma, pump, description)
            VALUES (%s, NOW(), %s, %s, %s, %s, %s)
        """, (cycle_id, device_id, states.get("power1"), states.get("power2"), states.get("power3"), description))
        conn.commit()
        logging.info(f"State saved to database: {states}, Description: {description}, Cycle: {cycle_id}")
    finally:
        conn.close()
