import sys
import os

# Add project root to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.sleeper_service import get_user_id

username = "thebmarv"
print(f"Attempting to find user_id for '{username}'...")

user_id = get_user_id(username)

if user_id:
    print(f"Successfully found user_id for '{username}': {user_id}")
else:
    print(f"Could not find user_id for '{username}'. The user may not exist or the Sleeper API might be unavailable.")
