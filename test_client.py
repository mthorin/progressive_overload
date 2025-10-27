import requests
import json

BASE_URL = "http://127.0.0.1:8000"  # Change this if your server runs elsewhere

def pp(response):
    """Pretty-print JSON responses."""
    print(f"\n➡️ {response.request.method} {response.request.url}")
    if response.request.body:
        print("Request body:", response.request.body)
    print("Status code:", response.status_code)
    try:
        print("Response JSON:", json.dumps(response.json(), indent=2))
    except Exception:
        print("Response text:", response.text)
    print("-" * 80)

def test_signup_login_logout():
    user_id = "test_user"
    password = "pass123"
    access_key = "l1h4f7d9_progressive"

    # Sign up
    resp = requests.post(f"{BASE_URL}/signup", json={
        "user_id": user_id,
        "password": password,
        "access_key": access_key
    })
    pp(resp)
    token = resp.json().get("authtoken", "")

    # Login
    resp = requests.put(f"{BASE_URL}/login", json={
        "user_id": user_id,
        "password": password
    })
    pp(resp)
    token = resp.json().get("authtoken", token)

    # Logout
    resp = requests.delete(f"{BASE_URL}/logout", json={"auth_token": token})
    pp(resp)
    return token

def test_add_edit_delete_workout(token):
    workout = {
        "id": 1,
        "sets": [[8, 60.0], [6, 65.0], [4, 70.0]],
        "name": "Bench Press",
        "increment": 2,
        "max_reps": 10,
        "min_reps": 4
    }

    # Add workout
    resp = requests.post(f"{BASE_URL}/workout/add", json={
        "auth_token": token,
        "workout": workout
    })
    pp(resp)

    # Edit workout
    workout["name"] = "Incline Bench Press"
    resp = requests.post(f"{BASE_URL}/workout/edit", json={
        "auth_token": token,
        "workout": workout
    })
    pp(resp)

    # Delete workout
    resp = requests.delete(f"{BASE_URL}/workout/delete", json={
        "auth_token": token,
        "workout_id": workout["id"]
    })
    pp(resp)

def test_add_edit_delete_split(token):
    split = {
        "name": "Push Day",
        "workouts": [1, 2, 3]
    }

    # Add split
    resp = requests.post(f"{BASE_URL}/split/add", json={
        "auth_token": token,
        "split": split
    })
    pp(resp)

    # Edit split
    split["name"] = "Upper Body"
    resp = requests.post(f"{BASE_URL}/split/edit", json={
        "auth_token": token,
        "split": split
    })
    pp(resp)

    # Delete split
    resp = requests.delete(f"{BASE_URL}/split/delete", json={
        "auth_token": token,
        "split_name": split["name"]
    })
    pp(resp)

def test_bulk_and_load(token):
    # Toggle bulk status
    resp = requests.put(f"{BASE_URL}/bulk/change", json={"auth_token": token})
    pp(resp)

    # Load state
    resp = requests.get(f"{BASE_URL}/load", json={"auth_token": token})
    pp(resp)

def test_start_and_set_complete(token):
    # Start workout
    resp = requests.put(f"{BASE_URL}/start_workout", json={"auth_token": token})
    pp(resp)

    # Complete set
    resp = requests.put(f"{BASE_URL}/set_complete", json={
        "auth_token": token,
        "diff": 3
    })
    pp(resp)

if __name__ == "__main__":
    print("🚀 Starting endpoint tests...")
    token = test_signup_login_logout()
    if token:
        test_add_edit_delete_workout(token)
        test_add_edit_delete_split(token)
        test_bulk_and_load(token)
        test_start_and_set_complete(token)
    else:
        print("❌ Could not obtain auth token — check /signup and /login endpoints.")
