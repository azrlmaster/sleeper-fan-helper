# Sleeper API Companion App

## 1. Project Overview

This project is a Flask-based backend application designed to be a companion for the [Sleeper](https://sleeper.com/) fantasy football platform. Its primary purpose is to help users determine which NFL teams and players they should be following on any given week.

It works by aggregating all of a user's fantasy players from across all of their Sleeper leagues. It then uses this aggregated roster to calculate a "score" for each NFL team, giving more weight to players who are in a user's starting lineup. The result is a ranked list of NFL teams that are most relevant to the user's fantasy football interests.

## 2. Features

*   **Roster Aggregation:** Automatically fetches and combines player rosters from all of a user's leagues for a given season.
*   **Starter vs. Bench Analysis:** Differentiates between players who are in a starting lineup versus those on the bench.
*   **Local Player Database:** Syncs a master list of all NFL players to a local SQLite database to ensure fast and efficient data retrieval.
*   **Team Ranking Engine:** Implements a weighted scoring algorithm to rank NFL teams based on the user's players.
*   **RESTful API:** Exposes a simple API endpoint to get all this information in a clean JSON format.

## 3. Setup and Installation

Follow these steps to get the application running locally.

### Prerequisites

*   Python 3.10+
*   `pip` for package installation

### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/azrlmaster/sleeper-fan-helper.git
    cd sleeper-fan-helper # Or your repository's root directory
    ```

2.  **Navigate to the Project Folder:**
    The application code is located in the `sleeper-companion-app` directory.
    ```bash
    cd sleeper-companion-app
    ```

3.  **Create a Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4.  **Install Dependencies:**
    All required Python packages are listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

## 4. Usage

Before running the application, you must initialize the local player database.

### Step 1: Initialize the Database

The application uses a local SQLite database to store player information. Run the following command from the `sleeper-companion-app` directory to create the database file and the `players` table.

```bash
python -m backend.utils.db
```
You should see the message: `Database initialized successfully.`

### Step 2: Sync Player Data

Next, you need to populate the database with the master list of all NFL players from the Sleeper API.

```bash
python -m backend.sync_players
```
This will take a moment and should end with a message like: `Synchronization complete. XXXXX players processed.` This step should be re-run periodically to keep the player list up to date.

### Step 3: Run the Web Server

Now you are ready to start the Flask development server.

```bash
# Make sure your terminal is in the sleeper-companion-app directory
export FLASK_APP=backend/app.py
flask run
```

The server will start, and you should see output indicating it is running on `http://127.0.0.1:5000`.

## 5. Testing the API

Once the server is running, you can test the API using a tool like `curl` or any API client.

### Health Check

First, test the `/health` endpoint to ensure the server is responsive.

**Request:**
```bash
curl http://127.0.0.1:5000/health
```

**Expected Response:**
A simple JSON object confirming the server is okay.
```json
{
  "status": "ok"
}
```

### Main Endpoint Test

Now, test the main functionality by requesting the aggregated roster for a specific Sleeper username. Replace `<username>` with a valid Sleeper username (e.g., `thebmarv`, `sleeper`).

**Request:**
```bash
curl http://127.0.0.1:5000/api/roster/thebmarv
```

**Expected Response:**
You will receive a large JSON object containing three main keys:
*   `user`: Information about the Sleeper user.
*   `roster`: A detailed list of all players on the user's teams.
*   `team_ranking`: A sorted list of NFL teams, ranked by their importance to the user.

**Example Snippet of the Response:**
```json
{
  "roster": [
    {
      "full_name": "Caleb Williams",
      "last_updated": "...",
      "leagues": [
        {
          "league_id": "1106395436690178048",
          "league_name": "Fugue State",
          "status": "bench"
        }
      ],
      "player_id": "11560",
      "position": "QB",
      "status": "Active",
      "team": "CHI",
      "years_exp": 1
    }
  ],
  "team_ranking": [
    {
      "bench": 1,
      "score": 7.0,
      "starters": 3,
      "team": "BUF"
    },
    {
      "bench": 0,
      "score": 6.0,
      "starters": 3,
      "team": "DAL"
    }
  ],
  "user": {
    "user_id": "736643501462269952",
    "username": "thebmarv"
  }
}
```
This confirms that the entire application is working correctly.
