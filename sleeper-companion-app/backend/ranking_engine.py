from collections import defaultdict
import sys
import os

# Add project root to path to allow imports from sibling directories.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.utils.db import get_db_connection

# --- Scoring Configuration ---
# These weights determine the value of a player being a starter vs. on the bench.
# A starter is considered twice as valuable for the "team to follow" score.
STARTER_WEIGHT = 2.0
BENCH_WEIGHT = 1.0

def calculate_team_scores(aggregated_roster):
    """
    Calculates a "score" for each NFL team based on a user's fantasy players.

    The algorithm iterates through a user's aggregated roster, queries the local
    database to find each player's real-life NFL team, and then assigns a score
    to that NFL team based on the player's status (starter or bench).

    Args:
        aggregated_roster (dict): A dictionary where keys are player_ids and
                                  values are lists of their statuses across leagues.

    Returns:
        list: A sorted list of dictionaries, where each dictionary represents an
              NFL team and its calculated score and player counts.
    """
    # defaultdict simplifies score accumulation. If a team isn't in the dict yet,
    # it's automatically created with a default value (a dict with 0s).
    team_scores = defaultdict(lambda: {"score": 0, "starters": 0, "bench": 0})

    # Get all unique player IDs from the roster for a single, efficient database query.
    player_ids = list(aggregated_roster.keys())
    if not player_ids:
        return []

    conn = None
    try:
        # Establish a connection to the SQLite database.
        conn = get_db_connection()
        cursor = conn.cursor()

        # Prepare the SQL query with a placeholder for each player ID.
        placeholders = ', '.join('?' for _ in player_ids)
        query = f"SELECT player_id, team FROM players WHERE player_id IN ({placeholders})"

        cursor.execute(query, player_ids)
        player_rows = cursor.fetchall()

        # Convert the list of DB rows into a player_id -> {player_info} map for fast lookups.
        player_map = {p['player_id']: p for p in player_rows}

        # Iterate through every player in the user's aggregated roster.
        for player_id, leagues in aggregated_roster.items():
            player_info = player_map.get(player_id)

            # Skip players who are not in our database or are not currently on an NFL team (e.g., Free Agents).
            if not player_info or not player_info["team"]:
                continue

            nfl_team = player_info["team"]

            # A player is considered a "starter" if they are starting in at least one of the user's leagues.
            is_starter = any(entry["status"] == "starter" for entry in leagues)

            # Add the appropriate weight to the NFL team's score.
            if is_starter:
                team_scores[nfl_team]["score"] += STARTER_WEIGHT
                team_scores[nfl_team]["starters"] += 1
            else:
                team_scores[nfl_team]["score"] += BENCH_WEIGHT
                team_scores[nfl_team]["bench"] += 1

    except Exception as e:
        print(f"Error in ranking engine: {e}")
        return []  # Return an empty list to prevent crashes in the main app.
    finally:
        if conn:
            conn.close()

    # Convert the defaultdict into a list of dictionaries for the final JSON response.
    sorted_teams = sorted(
        [{"team": team, **data} for team, data in team_scores.items()],
        key=lambda x: x["score"],
        reverse=True  # Sort from highest score to lowest.
    )

    return sorted_teams
