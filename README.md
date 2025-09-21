# Sleeper API Companion App

## 1. Project Overview

This project is a Flask-based application designed to be a companion for the [Sleeper](https://sleeper.com/) fantasy football platform. Its primary purpose is to help users determine which NFL teams and players they should be following on any given week.

It works by aggregating all of a user's fantasy players from across all of their Sleeper leagues. It then uses this aggregated roster to calculate a "score" for each NFL team, giving more weight to players who are in a user's starting lineup. The result is a ranked list of NFL teams that are most relevant to the user's fantasy football interests.

The application provides both a RESTful API and a simple web interface.

## 2. Features

*   **Web Interface:** A simple, clean UI to enter a Sleeper username and view the results.
*   **Roster Aggregation:** Automatically fetches and combines player rosters from all of a user's leagues for a given season.
*   **Starter vs. Bench Analysis:** Differentiates between players who are in a starting lineup versus those on the bench.
*   **Local Player Database:** Syncs a master list of all NFL players to a local SQLite database to ensure fast and efficient data retrieval.
*   **Team Ranking Engine:** Implements a weighted scoring algorithm to rank NFL teams based on the user's players.
*   **RESTful API:** Exposes a simple API endpoint to get all this information in a clean JSON format.
*   **Modular Structure:** Built with Flask Blueprints to allow for easy integration into other Flask applications.

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
    The application code is located in the `sleeper_companion_app` directory.
    ```bash
    cd sleeper_companion_app
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

The application uses a local SQLite database to store player information. Run the following command from the project's root directory (`sleeper-fan-helper`) to create the database file and the `players` table.

```bash
python -m sleeper_companion_app.backend.utils.db
```
You should see the message: `Database initialized successfully.`

### Step 2: Sync Player Data

Next, you need to populate the database with the master list of all NFL players from the Sleeper API.

```bash
python -m sleeper_companion_app.backend.sync_players
```
This will take a moment and should end with a message like: `Synchronization complete. XXXXX players processed.` This step should be re-run periodically to keep the player list up to date.

### Step 3: Run the Web Server

Now you are ready to start the Flask development server.

```bash
python sleeper_companion_app/run.py
```

The server will start, and you should see output indicating it is running on `http://127.0.0.1:5000`.

## 5. Using the Application

### Web Interface

Once the server is running, open your web browser and navigate to:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

You can enter a Sleeper username in the form and click "Analyze" to see the results.

### Testing the API

You can also test the API directly using a tool like `curl` or any API client.

#### Health Check

**Request:**
```bash
curl http://127.0.0.1:5000/health
```

**Expected Response:**
```json
{
  "status": "ok"
}
```

#### Main Endpoint Test

**Request:**
```bash
curl http://127.0.0.1:5000/api/roster/<username>
```
(Replace `<username>` with a valid Sleeper username)

**Expected Response:**
A JSON object containing the user's aggregated roster and the ranked list of NFL teams.
```json
{
  "roster": [ ... ],
  "team_ranking": [ ... ],
  "user": { ... }
}
```

## 6. Using as a Blueprint

This application is designed to be modular and can be integrated into an existing Flask application.

To use it as a blueprint, follow these steps:

1.  **Ensure the `sleeper_companion_app` is in your PYTHONPATH.**
    If your existing application is in the same project, this should work automatically.

2.  **Import the blueprint object** in your main application file:
    ```python
    from sleeper_companion_app.backend.main import main as sleeper_blueprint
    ```

3.  **Register the blueprint** with your Flask app instance. It is recommended to use a `url_prefix` to avoid route collisions with your existing app.
    ```python
    # In your app factory or main app file
    app.register_blueprint(sleeper_blueprint, url_prefix='/sleeper')
    ```

Now, all the routes from this application will be available under the `/sleeper` prefix. For example, the web interface will be at `http://<your-app-url>/sleeper/` and the API will be at `http://<your-app-url>/sleeper/api/roster/<username>`.
