from flask import Flask, jsonify
import sys
import os

# This allows the Flask app to be run from the project root (e.g., `flask run`)
# and still find the necessary modules in the `backend` directory.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import sleeper_service
from backend.utils.db import get_db_connection

# Initialize the Flask application.
# `instance_relative_config=True` allows the app to load config from an `instance` folder,
# which is a good practice for separating configuration from the application code.
app = Flask(__name__, instance_relative_config=True)

@app.route('/health')
def health_check():
    """
    A simple health check endpoint to confirm the server is running.
    Returns a 200 OK with a status message.
    """
    return {"status": "ok"}

@app.route('/api/roster/<username>')
def get_aggregated_roster(username):
    """
    The main API endpoint for the application.
    It takes a Sleeper username and returns a comprehensive JSON object containing:
    1. The user's details.
    2. A detailed list of all players on that user's rosters across all their leagues.
    3. A ranked list of NFL teams to follow based on the user's players.
    """
    # --- Step 1: User Identification ---
    # Translate the human-readable username into the stable user_id used by the API.
    user_id = sleeper_service.get_user_id(username)
    if not user_id:
        return jsonify({"error": f"User '{username}' not found"}), 404

    # --- Step 2: League & Roster Aggregation ---
    # Fetch all leagues for the user for a given season.
    # For this version, the season and week are hardcoded. A future version could make these dynamic.
    current_season = '2024'
    current_week = 1

    leagues = sleeper_service.get_leagues_for_user(user_id, current_season)
    if leagues is None:
        return jsonify({"error": "Failed to fetch leagues for user. The Sleeper API may be down."}), 502

    # This dictionary will hold the aggregated player data.
    # Key: player_id, Value: list of leagues the player is in and their status (starter/bench).
    aggregated_roster = {}

    # Iterate through each league to get roster and matchup data.
    for league in leagues:
        league_id = league['league_id']

        # Fetch all rosters and weekly matchups for the current league.
        rosters = sleeper_service.get_rosters_for_league(league_id)
        matchups = sleeper_service.get_matchups_for_league(league_id, current_week)

        # Handle cases where the API might fail for a specific league.
        if rosters is None or matchups is None:
            print(f"Warning: Could not process league {league_id} due to an API error. Skipping.")
            continue

        # Find the specific roster object belonging to our user.
        user_roster_obj = next((r for r in rosters if r.get('owner_id') == user_id), None)
        if not user_roster_obj:
            continue

        # Find the specific matchup object for the user's roster to determine starters.
        user_matchup_obj = next((m for m in matchups if m.get('roster_id') == user_roster_obj.get('roster_id')), None)

        # Extract all player IDs from the user's roster.
        all_player_ids = user_roster_obj.get('players', [])
        # Extract only the player IDs for the starters from the matchup data.
        starter_ids = user_matchup_obj.get('starters', []) if user_matchup_obj else []

        # Synthesize the data: for each player, record their status in this league.
        for player_id in all_player_ids:
            status = "starter" if player_id in starter_ids else "bench"

            # If this is the first time we've seen this player, initialize their entry.
            if player_id not in aggregated_roster:
                aggregated_roster[player_id] = []

            # Append the details for the current league.
            aggregated_roster[player_id].append({
                "league_id": league_id,
                "league_name": league['name'],
                "status": status
            })

    # --- Step 3: Data Enrichment & Ranking ---
    # Now that we have the aggregated roster, enrich it with details from our local DB.
    player_ids = list(aggregated_roster.keys())

    conn = get_db_connection()

    detailed_roster = []
    if player_ids:
        # Create a SQL query with the correct number of placeholders for the player IDs.
        placeholders = ', '.join('?' for _ in player_ids)
        query = f"SELECT * FROM players WHERE player_id IN ({placeholders})"

        # Execute the query and fetch all results.
        cursor = conn.cursor()
        cursor.execute(query, player_ids)
        player_rows = cursor.fetchall()
        # Convert the list of database rows into a dictionary for quick lookups.
        player_map = {p['player_id']: dict(p) for p in player_rows}

        # Combine the aggregated roster status with the detailed player info from the DB.
        for pid, data in aggregated_roster.items():
            player_details = player_map.get(pid, {"player_id": pid, "full_name": "Unknown Player"})
            player_details['leagues'] = data
            detailed_roster.append(player_details)

    conn.close()

    # Calculate the final team rankings using the ranking engine.
    # We import here to avoid potential circular dependencies at startup.
    from backend import ranking_engine
    team_ranking = ranking_engine.calculate_team_scores(aggregated_roster)

    # --- Step 4: Final Response ---
    # Assemble the final, comprehensive JSON object to be returned to the client.
    final_response = {
        "user": {
            "username": username,
            "user_id": user_id
        },
        "roster": detailed_roster,
        "team_ranking": team_ranking
    }

    return jsonify(final_response)

if __name__ == '__main__':
    # For development, it's better to run the app using the `flask run` command.
    # This ensures the development server is used with all its features (like debugging and auto-reloading).
    app.run(debug=True)
