from flask import jsonify, render_template, current_app
from . import main
import datetime
from .. import sleeper_service, ranking_engine
from ..utils.db import get_db_connection

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/health')
def health_check():
    return {"status": "ok"}

@main.route('/api/roster/<username>')
def get_aggregated_roster(username):
    user_id = sleeper_service.get_user_id(username)
    if not user_id:
        return jsonify({"error": f"User '{username}' not found"}), 404

    current_season = str(datetime.datetime.now().year)
    current_app.logger.info(f"Fetching data for user '{username}' for season '{current_season}'")
    current_week = 1
    leagues = sleeper_service.get_leagues_for_user(user_id, current_season)
    if leagues is None:
        return jsonify({"error": "Failed to fetch leagues for user."}), 502

    aggregated_roster = {}
    for league in leagues:
        league_id = league['league_id']
        rosters = sleeper_service.get_rosters_for_league(league_id)
        matchups = sleeper_service.get_matchups_for_league(league_id, current_week)
        if rosters is None or matchups is None:
            continue

        user_roster_obj = next((r for r in rosters if r.get('owner_id') == user_id), None)
        if not user_roster_obj:
            continue

        user_matchup_obj = next((m for m in matchups if m.get('roster_id') == user_roster_obj.get('roster_id')), None)
        all_player_ids = user_roster_obj.get('players', [])
        starter_ids = user_matchup_obj.get('starters', []) if user_matchup_obj else []

        for player_id in all_player_ids:
            status = "starter" if player_id in starter_ids else "bench"
            if player_id not in aggregated_roster:
                aggregated_roster[player_id] = []
            aggregated_roster[player_id].append({
                "league_id": league_id,
                "league_name": league['name'],
                "status": status
            })

    player_ids = list(aggregated_roster.keys())
    conn = get_db_connection()
    detailed_roster = []
    if player_ids:
        placeholders = ', '.join('?' for _ in player_ids)
        query = f"SELECT * FROM players WHERE player_id IN ({placeholders})"
        cursor = conn.cursor()
        cursor.execute(query, player_ids)
        player_rows = cursor.fetchall()
        player_map = {p['player_id']: dict(p) for p in player_rows}

        for pid, data in aggregated_roster.items():
            player_details = player_map.get(pid, {"player_id": pid, "full_name": "Unknown Player"})
            player_details['leagues'] = data
            detailed_roster.append(player_details)
    conn.close()

    team_ranking = ranking_engine.calculate_team_scores(aggregated_roster)

    final_response = {
        "user": {"username": username, "user_id": user_id},
        "roster": detailed_roster,
        "team_ranking": team_ranking
    }
    return jsonify(final_response)
