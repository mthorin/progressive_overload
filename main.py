from fastapi import FastAPI, Body, HTTPException
from starlette.middleware.cors import CORSMiddleware

from workout_database import WorkoutDatabase

CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

app = FastAPI()
app.add_middleware(CORSMiddleware, **CORS_CONFIG)

db = WorkoutDatabase()

@app.put("/login")
def log_in():
    # check credentials, return auth_token
    return_info() # with auth token
    # send info and authtoken to client
    pass

@app.delete("/logout")
def log_out():
    # delete authtoken
    pass

def return_info():
    # get the users info from the database
    pass

def check_auth(auth: str):
    return db.check_auth_token(auth)
    

@app.put("/start_workout")
def start_workout():
    check_auth()
    # change state saved in db
    pass

@app.put("/set_complete")
def set_complete():
    check_auth()
    # update database based on heuristics
    # change state saved in db
    # return info?
    pass

@app.put("/update_workout")
def update_workout():
    check_auth()
    pass

@app.post("/signup")
def sign_up():
    # create new user in database
    pass

@app.get("/load")
def load_state():
    # get the current state (return_info)
    return_info()
    # if appropriate, get the current workout
    # return
    pass