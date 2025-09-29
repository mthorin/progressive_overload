from fastapi import FastAPI, Body, HTTPException
from typing import Union, Annotated
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from workout_database import WorkoutDatabase

CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

class Workout(BaseModel):
    sets: list[tuple[int, int]]
    name: str
    increment: int
    max_reps: int
    min_reps: int

app = FastAPI()
app.add_middleware(CORSMiddleware, **CORS_CONFIG)

db = WorkoutDatabase()

@app.put("/login")
def log_in(user_id: Annotated[str, Body()], password: Annotated[str, Body()]):
    """
    Takes in a user id and password, returns a new authtoken for the session.
    """
    auth_token = db.log_in_user(user_id, password)

    if not auth_token:
        return { "message" : "failure" , "authtoken" : "" }
    
    return { "message" : "success" , "authtoken" : auth_token }

@app.delete("/logout")
def log_out(auth_token: Annotated[str, Body()]):
    """
    Takes in a authtoken, deletes the authtoken from the database.
    """
    db.log_out_user(auth_token)

    return { "message" : "success" }

@app.post("/signup")
def sign_up(user_id: Annotated[str, Body()], password: Annotated[str, Body()], access_key: Annotated[str, Body()]):
    """
    Takes in a user id, password, and access key and returns a new authtoken for the session and creates an entry for the user in the database.
    """
    if access_key is not 'l1h4f7d9_progressive':
        return { "message" : "failure" , "authtoken" : "" }

    auth_token = db.create_user(user_id, password)

    if not auth_token:
        return { "message" : "failure" , "authtoken" : "" }

    return { "message" : "success" , "authtoken" : auth_token }

def return_info():
    # get the users info from the database
    pass

@app.put("/start_workout")
def start_workout(auth_token: Annotated[str, Body()]):
    """
    Takes in an authtoken, tells the database to start the workout.
    """
    user_id = db.check_auth_token(auth_token)
    if not user_id:
        return { "message" : "failure" }
    
    state = db.get_state(user_id)
    if state is not 'inactive':
        return { "message" : "failure" }
    
    db.initiate_workout(user_id)

    return { "message" : "success" }

@app.put("/set_complete")
def set_complete(auth_token: Annotated[str, Body()], diff: Annotated[int, Body()]):
    """
    Takes in an authtoken and the difficulty report, updates the workout based on internal heuristsics, tells the database to set is over.
    """
    user_id = db.check_auth_token(auth_token)
    if not user_id:
        return { "message" : "failure" }
    
    state = db.get_state(user_id)
    if state is not 'mid_set':
        return { "message" : "failure" }
    
    workout = db.get_current_workout(user_id)
    # update database based on heuristics
    db.update_workout_by_id(workout.id, workout)

    db.complete_set(user_id)

    return { "message" : "success" }

@app.post("/update_workout")
def update_workout(auth_token: Annotated[str, Body()], workout: Workout):
    
    user_id = db.check_auth_token(auth_token)
    if not user_id:
        return { "message" : "failure" }
    
    # fill
    return { "message" : "success" }

@app.get("/load")
def load_state(auth_token: Annotated[str, Body()]):
    # get the current state (return_info)
    return_info()
    # if appropriate, get the current workout
    # return
    pass