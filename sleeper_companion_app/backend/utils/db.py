import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root.
# This allows the database path to be configured without hardcoding it.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Get the database path from environment variables, with a sensible default.
DATABASE_URL = os.getenv("DATABASE_URL", "instance/sleeper.db")
# Determine the directory where the database file is stored.
INSTANCE_FOLDER = os.path.dirname(DATABASE_URL)

def get_db_connection():
    """
    Establishes and returns a connection to the SQLite database.

    This function ensures the directory for the database exists and configures
    the connection to return rows that can be accessed by column name (like a dict).

    Returns:
        sqlite3.Connection: A connection object to the database.
    """
    # Construct the full, absolute path to the database file.
    # This is important to ensure the app can find the DB regardless of where
    # the script is run from.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    db_path = os.path.join(project_root, DATABASE_URL)

    # Ensure the 'instance' folder exists before trying to connect.
    instance_path = os.path.dirname(db_path)
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    conn = sqlite3.connect(db_path)
    # This line is crucial for accessing query results like dictionaries
    # (e.g., row['column_name']) instead of by index (e.g., row[0]).
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database by creating the 'players' table if it doesn't already exist.
    This is intended to be run once during setup.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # The schema for the 'players' table.
    # player_id is the PRIMARY KEY to ensure uniqueness.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id TEXT PRIMARY KEY,
            full_name TEXT,
            team TEXT,
            position TEXT,
            years_exp INTEGER,
            status TEXT,
            last_updated TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    # This allows the database to be initialized by running the script directly
    # from the command line, e.g., `python -m backend.utils.db`
    init_db()
