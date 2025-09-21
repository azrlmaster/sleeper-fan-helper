# **Detailed Development Plan: Sleeper API Companion App**

This document provides a comprehensive, phased development plan for the Sleeper API-powered fantasy football companion app. It is tailored for a Python backend (using the Flask framework), deployment on PythonAnywhere, and secure configuration management using a .env file.

## **Phase 0: Project Setup & Environment Configuration**

This foundational phase ensures the local development environment and project structure are correctly configured before writing any application code.

### **1\. Local Environment Setup**

* **Create Project Directory:**  
  mkdir sleeper-companion-app  
  cd sleeper-companion-app

* **Create Python Virtual Environment:** This isolates the project's dependencies.  
  python3 \-m venv venv  
  source venv/bin/activate  \# On Windows use \`venv\\Scripts\\activate\`

* **Install Initial Dependencies:**  
  pip install Flask python-dotenv pymongo sleeper-py gunicorn

* **Create requirements.txt:** Freeze your initial dependencies into a file that PythonAnywhere will use.  
  pip freeze \> requirements.txt

### **2\. Project Directory Structure**

Create the following file and folder structure. This separates concerns and follows best practices.

sleeper-companion-app/  
│  
├── .env                  \# For environment variables (DO NOT COMMIT TO GIT)  
├── .gitignore            \# To ignore venv, .env, \_\_pycache\_\_, etc.  
├── requirements.txt      \# List of Python dependencies  
│  
└── backend/  
    ├── \_\_init\_\_.py         \# Makes the backend directory a Python package  
    ├── app.py              \# Main Flask application file  
    ├── sleeper\_service.py  \# Module for all Sleeper API interactions  
    ├── ranking\_engine.py   \# Module for the "Teams to Follow" algorithm  
    └── utils/  
        └── db.py           \# MongoDB connection and helper functions

### **3\. Configuration Files**

* **.env File:** Create this file in the root directory. You will get your MongoDB connection string from a service like MongoDB Atlas.  
  \# .env  
  FLASK\_ENV=development  
  MONGO\_URI="mongodb+srv://\<user\>:\<password\>@\<cluster-url\>/\<db-name\>?retryWrites=true\&w=majority"

* **.gitignore File:** Create this to prevent sensitive information and unnecessary files from being tracked by Git.  
  \# .gitignore  
  venv/  
  .env  
  \_\_pycache\_\_/  
  \*.pyc

## **Phase 1: Data Pipeline & Backend Foundation (Weeks 1-2)**

**Objective:** Build the core data engine by fetching, storing, and creating a reliable synchronization mechanism for the master player list, as outlined in the architectural blueprint \[cite: 4.1\].

### **1\. Initialize Flask App & Database Connection**

* **backend/utils/db.py:** Set up the MongoDB connection.  
  \# backend/utils/db.py  
  import os  
  from pymongo import MongoClient  
  from dotenv import load\_dotenv

  load\_dotenv() \# Load variables from .env file

  MONGO\_URI \= os.getenv("MONGO\_URI")  
  client \= MongoClient(MONGO\_URI)  
  db \= client.get\_database("sleeper\_companion") \# Or your chosen DB name  
  players\_collection \= db.get\_collection("players")

* **backend/app.py:** Create the basic Flask application.  
  \# backend/app.py  
  from flask import Flask

  app \= Flask(\_\_name\_\_)

  @app.route('/health')  
  def health\_check():  
      return {"status": "ok"}

  if \_\_name\_\_ \== '\_\_main\_\_':  
      app.run(debug=True)

### **2\. Implement Sleeper Service Layer**

* **backend/sleeper\_service.py:** This module will encapsulate all direct communication with the Sleeper API, as recommended in the blueprint \[cite: 2.2.2\]. It will use the sleeper-py library.  
  \# backend/sleeper\_service.py  
  from sleeper\_py import Players, User, League

  def get\_all\_players():  
      """Fetches the entire dataset of NFL players."""  
      players \= Players()  
      return players.get\_all\_players()

  def get\_user\_id(username):  
      """Translates a username to a user\_id."""  
      try:  
          user \= User(username)  
          return user.get\_user()\['user\_id'\]  
      except Exception:  
          return None

  def get\_leagues\_for\_user(user\_id, season='2024'):  
      """Gets all leagues for a user for a given season."""  
      user \= User(user\_id\_or\_name=user\_id)  
      return user.get\_leagues(sport="nfl", season=season)

  def get\_rosters\_for\_league(league\_id):  
      """Gets all rosters in a specific league."""  
      league \= League(league\_id)  
      return league.get\_rosters()

  def get\_matchups\_for\_league(league\_id, week):  
      """Gets matchup data to determine starters."""  
      league \= League(league\_id)  
      return league.get\_matchups(week)

### **3\. Create the Player Data Synchronization Script**

* Create a new file backend/sync\_players.py. This script will be run daily to update your local player database, a critical architectural requirement \[cite: 1.3\].  
  \# backend/sync\_players.py  
  from backend.utils.db import players\_collection  
  from backend.sleeper\_service import get\_all\_players  
  from pymongo import UpdateOne  
  import datetime

  def run\_sync():  
      print("Starting player data synchronization...")  
      try:  
          all\_players\_data \= get\_all\_players()  
          if not all\_players\_data:  
              print("Failed to fetch players from API.")  
              return

          update\_operations \= \[\]  
          for player\_id, player\_data in all\_players\_data.items():  
              \# Prepare data for MongoDB  
              player\_doc \= {  
                  "player\_id": player\_id,  
                  "full\_name": player\_data.get("full\_name"),  
                  "team": player\_data.get("team"),  
                  "position": player\_data.get("position"),  
                  "years\_exp": player\_data.get("years\_exp"),  
                  "status": player\_data.get("status"),  
                  "last\_updated": datetime.datetime.utcnow()  
              }  
              update\_operations.append(  
                  UpdateOne(  
                      {"player\_id": player\_id},  
                      {"$set": player\_doc},  
                      upsert=True  
                  )  
              )

          if update\_operations:  
              result \= players\_collection.bulk\_write(update\_operations)  
              print(f"Synchronization complete. Matched: {result.matched\_count}, Upserted: {result.upserted\_count}")  
          else:  
              print("No players to update.")

      except Exception as e:  
          print(f"An error occurred during synchronization: {e}")

  if \_\_name\_\_ \== "\_\_main\_\_":  
      run\_sync()

### **4\. Initial Population & Scheduling on PythonAnywhere**

* **Run Initial Population:** From your terminal (with the virtual environment active), run the script once to populate the database.  
  python \-m backend.sync\_players

* **Schedule Daily Task on PythonAnywhere:**  
  1. Log in to your PythonAnywhere account.  
  2. Go to the **"Tasks"** tab.  
  3. Under "Scheduled tasks," set a time (e.g., a UTC time like 08:00, which is during off-peak US hours).  
  4. In the command box, enter the full path to your Python executable and script:  
     /home/\<YourUsername\>/.virtualenvs/\<YourVirtualenvName\>/bin/python /home/\<YourUsername\>/\<YourProjectFolder\>/backend/sync\_players.py

  5. Click "Create" to save the task. This fulfills the mandatory requirement for a daily data refresh \[cite: 1.3, 4.1\].

## **Phase 2: Core Aggregation Logic (Weeks 3-4)**

**Objective:** Implement the backend endpoint that accepts a username and returns a fully aggregated roster with starter/bench status \[cite: 4.2\].

### **1\. Create the Primary API Endpoint**

* **backend/app.py:** Add the new route and logic.  
  \# backend/app.py (additions)  
  from flask import Flask, jsonify, request  
  from backend import sleeper\_service  
  import datetime

  \# ... (keep existing Flask app setup)

  @app.route('/api/roster/\<username\>')  
  def get\_aggregated\_roster(username):  
      \# Step 1: User Identification \[cite: 1.2\]  
      user\_id \= sleeper\_service.get\_user\_id(username)  
      if not user\_id:  
          return jsonify({"error": "User not found"}), 404

      \# Step 2: League Discovery \[cite: 1.2\]  
      \# For now, we'll hardcode the current season and week  
      current\_season \= '2024'  
      current\_week \= 1 \# This would ideally be determined dynamically  
      leagues \= sleeper\_service.get\_leagues\_for\_user(user\_id, current\_season)

      aggregated\_roster \= {}

      for league in leagues:  
          league\_id \= league\['league\_id'\]  
          rosters \= sleeper\_service.get\_rosters\_for\_league(league\_id)  
          matchups \= sleeper\_service.get\_matchups\_for\_league(league\_id, current\_week)

          \# Find the user's specific roster and matchup  
          user\_roster\_obj \= next((r for r in rosters if r\['owner\_id'\] \== user\_id), None)  
          user\_matchup\_obj \= next((m for m in matchups if m.get('roster\_id') \== user\_roster\_obj\['roster\_id'\]), None)

          if not user\_roster\_obj:  
              continue

          \# Step 3 & 4: Aggregate players and find starters \[cite: 1.2\]  
          all\_player\_ids \= user\_roster\_obj.get('players', \[\])  
          starter\_ids \= user\_matchup\_obj.get('starters', \[\]) if user\_matchup\_obj else \[\]

          \# Step 5: Data Synthesis and Differentiation \[cite: 1.2\]  
          for player\_id in all\_player\_ids:  
              status \= "starter" if player\_id in starter\_ids else "bench"

              \# To handle players across multiple leagues, store a list of statuses  
              if player\_id not in aggregated\_roster:  
                  aggregated\_roster\[player\_id\] \= \[\]

              aggregated\_roster\[player\_id\].append({  
                  "league\_id": league\_id,  
                  "league\_name": league\['name'\],  
                  "status": status  
              })

      return jsonify(aggregated\_roster)

### **2\. Local Testing**

* Run the Flask development server:  
  python \-m backend.app

* Use a tool like curl or your web browser to test the endpoint:  
  curl \[http://127.0.0.1:5000/api/roster/sleeperuser\](http://127.0.0.1:5000/api/roster/sleeperuser)

  This integration test validates that the backend produces the correct data structure, a key goal of this phase \[cite: 4.2\].

## **Phase 3: Ranking Algorithm & UI (Weeks 5-7)**

**Objective:** Implement the "Teams to Follow" feature and build the final user interface \[cite: 4.3\].

### **1\. Implement the Ranking Engine**

* **backend/ranking\_engine.py:** Create the V1.0 algorithm as a modular service \[cite: 2.2.3, 4.3\].  
  \# backend/ranking\_engine.py  
  from collections import defaultdict  
  from backend.utils.db import players\_collection

  STARTER\_WEIGHT \= 2.0  
  BENCH\_WEIGHT \= 1.0

  def calculate\_team\_scores(aggregated\_roster):  
      team\_scores \= defaultdict(lambda: {"score": 0, "starters": 0, "bench": 0})

      \# Get all unique player IDs for a single DB query  
      player\_ids \= list(aggregated\_roster.keys())  
      player\_docs \= players\_collection.find({"player\_id": {"$in": player\_ids}})

      \# Create a quick lookup map  
      player\_map \= {p\["player\_id"\]: p for p in player\_docs}

      for player\_id, leagues in aggregated\_roster.items():  
          player\_info \= player\_map.get(player\_id)  
          if not player\_info or not player\_info.get("team"):  
              continue \# Skip players with no team (e.g., Free Agents)

          nfl\_team \= player\_info\["team"\]

          \# Use the 'best' status across all leagues (starter \> bench)  
          is\_starter \= any(entry\["status"\] \== "starter" for entry in leagues)

          if is\_starter:  
              team\_scores\[nfl\_team\]\["score"\] \+= STARTER\_WEIGHT  
              team\_scores\[nfl\_team\]\["starters"\] \+= 1  
          else:  
              team\_scores\[nfl\_team\]\["score"\] \+= BENCH\_WEIGHT  
              team\_scores\[nfl\_team\]\["bench"\] \+= 1

      \# Format and sort the results  
      sorted\_teams \= sorted(  
          \[{"team": team, \*\*data} for team, data in team\_scores.items()\],  
          key=lambda x: x\["score"\],  
          reverse=True  
      )

      return sorted\_teams

### **2\. Integrate Ranking into the API Response**

* **backend/app.py:** Update the endpoint to call the ranking engine.  
  \# backend/app.py (updates to get\_aggregated\_roster)  
  from backend import ranking\_engine \# Add this import  
  from backend.utils.db import players\_collection \# Add this import

  @app.route('/api/roster/\<username\>')  
  def get\_aggregated\_roster(username):  
      \# ... (all previous logic to build aggregated\_roster) ...

      \# After building the aggregated\_roster dictionary:

      \# Fetch full player details for the response  
      player\_ids \= list(aggregated\_roster.keys())  
      player\_docs \= players\_collection.find({"player\_id": {"$in": player\_ids}}, {'\_id': 0})  
      player\_map \= {p\["player\_id"\]: p for p in player\_docs}

      \# Combine roster status with player details  
      detailed\_roster \= \[\]  
      for pid, data in aggregated\_roster.items():  
          player\_details \= player\_map.get(pid, {})  
          player\_details\['leagues'\] \= data  
          detailed\_roster.append(player\_details)

      \# Calculate team rankings \[cite: 4.3\]  
      team\_ranking \= ranking\_engine.calculate\_team\_scores(aggregated\_roster)

      final\_response \= {  
          "user": {  
              "username": username,  
              "user\_id": user\_id  
          },  
          "roster": detailed\_roster,  
          "team\_ranking": team\_ranking  
      }

      return jsonify(final\_response)

## **Phase 4: Deployment & Maintenance (Week 8\)**

**Objective:** Deploy the application to PythonAnywhere and set up monitoring \[cite: 4.4\].

### **1\. Prepare for Deployment**

* **Finalize requirements.txt:** pip freeze \> requirements.txt  
* **Git:** Initialize a git repository, commit your code, and push it to a provider like GitHub.

### **2\. Deploy to PythonAnywhere**

* **Bash Console:** Open a Bash console on PythonAnywhere.  
  * git clone \<your-repo-url\>  
  * cd \<your-project-folder\>  
  * mkvirtualenv \--python=/usr/bin/python3.10 my-virtualenv (or desired Python version)  
  * pip install \-r requirements.txt  
* **Web Tab:**  
  1. Click "Add a new web app".  
  2. Select "Manual configuration" and your desired Python version.  
  3. **Code Location:** Set the "Source code" path to your project directory (e.g., /home/\<username\>/sleeper-companion-app).  
  4. **Virtualenv:** Set the path to the virtualenv you created (e.g., /home/\<username\>/.virtualenvs/my-virtualenv).  
  5. **WSGI Configuration:** Click the link to the WSGI file and edit it to point to your Flask app instance. It should look like this:  
     import sys  
     import os

     \# Add your project directory to the python path  
     path \= '/home/\<YourUsername\>/sleeper-companion-app'  
     if path not in sys.path:  
         sys.path.insert(0, path)

     \# Change directory to your app's folder  
     os.chdir(path)

     \# Import your Flask app object  
     from backend.app import app as application

  6. **Environment Variables:** In the "Web" tab, scroll down to the "Environment variables" section. Add your MONGO\_URI here. This is the secure, production way to handle your .env file content.  
* **Reload App:** Click the big "Reload" button on the "Web" tab. Your API should now be live at \<YourUsername\>.pythonanywhere.com.

### **3\. Deploy Frontend (React)**

For the React frontend, you will build it locally and upload the static files.

* **Local Build:** npm run build  
* **PythonAnywhere:**  
  1. In the "Web" tab, go to the "Static files" section.  
  2. Add a new entry:  
     * **URL:** /  
     * **Path:** /home/\<YourUsername\>/\<YourProjectFolder\>/frontend/build (adjust path as needed).  
  3. Upload the contents of your local build folder to the corresponding directory on PythonAnywhere using its "Files" tab.  
  4. Reload the web app.

### **4\. Final Checks and Monitoring**

* **Verify Scheduled Task:** Go to the "Tasks" tab and check the logs for your sync script to ensure it's running correctly in the production environment \[cite: 4.4\].  
* **Monitor Logs:** Use the **Error log** and **Server log** links on the "Web" tab to monitor your live application for any issues \[cite: 4.4\]. These logs are your primary tool for troubleshooting on PythonAnywhere.