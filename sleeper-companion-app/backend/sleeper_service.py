import requests

# The base URL for all v1 Sleeper API endpoints.
BASE_URL = "https://api.sleeper.app/v1"

def _make_request(url):
    """
    A centralized helper function to make GET requests to the Sleeper API.
    It handles common tasks like checking for successful responses and parsing JSON.

    Args:
        url (str): The full URL to request.

    Returns:
        dict or list or None: The parsed JSON response, or None if the request fails.
    """
    try:
        response = requests.get(url, timeout=10) # Adding a timeout is good practice.
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx).
        return response.json()
    except requests.exceptions.RequestException as e:
        # This will catch connection errors, timeouts, etc.
        print(f"API request failed for URL {url}: {e}")
        return None

def get_all_players():
    """
    Fetches the entire dataset of all NFL players from the Sleeper API.
    This is a large dataset and is intended to be synced to a local database periodically.
    """
    url = f"{BASE_URL}/players/nfl"
    return _make_request(url)

def get_user_id(username):
    """
    Translates a human-readable Sleeper username into its permanent user_id.

    Args:
        username (str): The Sleeper username.

    Returns:
        str or None: The user_id if found, otherwise None.
    """
    url = f"{BASE_URL}/user/{username}"
    data = _make_request(url)
    if data and 'user_id' in data:
        return data['user_id']
    return None

def get_leagues_for_user(user_id, season='2024'):
    """
    Gets all fantasy football leagues for a specific user for a given season.

    Args:
        user_id (str): The user's unique ID.
        season (str): The year of the season to fetch leagues for.

    Returns:
        list or None: A list of league objects, or None on failure.
    """
    url = f"{BASE_URL}/user/{user_id}/leagues/nfl/{season}"
    return _make_request(url)

def get_rosters_for_league(league_id):
    """
    Gets all team rosters for a specific league. Each roster object contains
    a list of player_ids.

    Args:
        league_id (str): The league's unique ID.

    Returns:
        list or None: A list of roster objects, or None on failure.
    """
    url = f"{BASE_URL}/league/{league_id}/rosters"
    return _make_request(url)

def get_matchups_for_league(league_id, week):
    """
    Gets all weekly matchups for a specific league. This data is crucial
    for determining which players were in the starting lineup.

    Args:
        league_id (str): The league's unique ID.
        week (int): The week of the season to fetch matchups for.

    Returns:
        list or None: A list of matchup objects, or None on failure.
    """
    url = f"{BASE_URL}/league/{league_id}/matchups/{week}"
    return _make_request(url)
