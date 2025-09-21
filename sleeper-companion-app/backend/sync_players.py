import datetime
import sys
import os

# This is to ensure the script can find the 'backend' module when run directly
# It adds the project root (`sleeper-companion-app`) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.utils.db import get_db_connection
from backend.sleeper_service import get_all_players

def run_sync():
    """
    Fetches player data from the Sleeper API and syncs it with the local SQLite database.
    """
    print("Starting player data synchronization...")
    conn = None
    try:
        all_players_data = get_all_players()
        if not all_players_data:
            print("Failed to fetch players from API.")
            return

        player_list = []
        for player_id, p_data in all_players_data.items():
            # Ensure years_exp is an integer or None
            years_exp = p_data.get("years_exp")
            try:
                years_exp = int(years_exp) if years_exp is not None else None
            except (ValueError, TypeError):
                years_exp = None # Or a default value like 0

            player_list.append((
                player_id,
                p_data.get("full_name"),
                p_data.get("team"),
                p_data.get("position"),
                years_exp,
                p_data.get("status"),
                datetime.datetime.utcnow().isoformat()
            ))

        if not player_list:
            print("No players to update.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        # Use INSERT OR REPLACE to add new players or update existing ones
        sql = """
            INSERT OR REPLACE INTO players (
                player_id, full_name, team, position, years_exp, status, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        cursor.executemany(sql, player_list)
        conn.commit()

        print(f"Synchronization complete. {cursor.rowcount} players processed.")

    except Exception as e:
        print(f"An error occurred during synchronization: {e}")
        # For debugging, print traceback
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_sync()
