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
    id: int
    sets: list[tuple[float, float]]
    name: str
    increment: int
    max_reps: int
    min_reps: int

class Split(BaseModel):
    name: str
    workouts: list[int]

class LoadResult(BaseModel):
    state: str
    workout: Workout | None = None
    curr_day: int | None = None
    all_workouts: list[Workout] | None = None
    completed: list[bool] | None = None

app = FastAPI()
app.add_middleware(CORSMiddleware, **CORS_CONFIG)

# Message defaults
AUTH_FAIL = "invalid auth"
SUCCESS = "success"
BAD_STATE = "incorrect state"
NOT_FOUND = "item not found"

db = WorkoutDatabase()

@app.put("/login")
def log_in(user_id: Annotated[str, Body()], password: Annotated[str, Body()]):
    """
    Takes in a user id and password, returns a new authtoken for the session.
    """
    auth_token = db.log_in_user(user_id, password)

    if not auth_token:
        return { "message" : AUTH_FAIL , "authtoken" : "" }
    
    return { "message" : SUCCESS , "authtoken" : auth_token }

@app.delete("/logout")
def log_out(auth_token: Annotated[str, Body()]):
    """
    Takes in a authtoken, deletes the authtoken from the database.
    """
    db.log_out_user(auth_token)

    return { "message" : SUCCESS }

@app.post("/signup")
def sign_up(user_id: Annotated[str, Body()], password: Annotated[str, Body()], access_key: Annotated[str, Body()]):
    """
    Takes in a user id, password, and access key and returns a new authtoken for the session and creates an entry for the user in the database.
    """
    if access_key is not 'l1h4f7d9_progressive':
        return { "message" : "invalid key" , "authtoken" : "" }

    auth_token = db.create_user(user_id, password)

    if not auth_token:
        return { "message" : "invalid username" , "authtoken" : "" }

    return { "message" : SUCCESS , "authtoken" : auth_token }

@app.put("/start_workout")
def start_workout(auth_token: Annotated[str, Body()]):
    """
    Takes in an authtoken, tells the database to start the workout.
    """
    user_id = db.check_auth_token(auth_token)
    if not user_id:
        return { "message" : AUTH_FAIL }
    
    state = db.get_state(user_id)
    if state is not 'inactive':
        return { "message" : BAD_STATE }
    
    db.initiate_workout(user_id)

    return { "message" : SUCCESS }

def increment_workout(workout: Workout, incre = 1, cycles = 1):
    for _ in range(cycles):
        lowest_reps, lowest_weight = workout.sets[-1]
        for i in range(len(workout.sets) + 1):
            reps, weight = workout.sets[len(workout.sets) - 1 - i]
            if reps > lowest_reps or weight > lowest_weight:
                break

        new_reps = lowest_reps
        new_weight = lowest_weight

        if lowest_reps >= workout.max_reps:
            new_reps = workout.min_reps
            new_weight += workout.increment
        else:
            new_reps += incre

        workout.sets[len(workout.sets) - i] = (new_reps, new_weight)

    return workout

def decrement_workout(workout: Workout, incre = 1, cycles = 1):
    for _ in range(cycles):
        high_reps, high_weight = workout.sets[0]
        for i in range(len(workout.sets) + 1):
            reps, weight = workout.sets[i%len(workout.sets)]
            if weight < high_weight or reps < high_reps:
                break
        
        new_reps = high_reps
        new_weight = high_weight

        if high_reps <= workout.min_reps:
            new_reps = workout.max_reps
            new_weight -= workout.increment
        else:
            new_reps -= incre

        workout.sets[i - 1] = (new_reps, new_weight)
    
    return workout

@app.put("/set_complete")
def set_complete(auth_token: Annotated[str, Body()], diff: Annotated[int, Body()]):
    """
    Takes in an authtoken and the difficulty report, updates the workout based on internal heuristsics, tells the database to set is over.
    """
    user_id = db.check_auth_token(auth_token)
    if not user_id:
        return { "message" : AUTH_FAIL }
    
    state = db.get_state(user_id)
    if state is not 'mid_set':
        return { "message" : BAD_STATE }
    
    if diff > 10:
        return { "message" : "difficulty value outside of range" }
    
    workout = db.get_current_workout(user_id)

    # update database based on heuristics
    """
    lower  all sets -1
    -3     two sets -2
    -2     one set -1
    -1     keep weight
     0~ 1  up weight / All sets +1
     2~ 4  All sets +1 / two sets +1
     5~ 7  Two set +1  / One set +1
     8~10  One set +1  / One set +1/2
    """
    bulk = db.check_bulk_status(user_id)
    if not bulk and diff >= 8:
        workout = increment_workout(workout, incre=.5)
    elif (bulk and diff >= 8) or (not bulk and diff >= 5):
        workout = increment_workout(workout)
    elif (bulk and diff >= 5) or (not bulk and diff >= 2):
        workout = increment_workout(workout, cycles=2)
    elif (bulk and diff >= 2) or (not bulk and diff >= 0):
        workout = increment_workout(workout, cycles=len(workout.sets))
    elif bulk and diff >= 0:
        for i in range(len(workout.sets)):
            workout.sets[i] = (workout.sets[i][0], workout.sets[i][1] + workout.increment)
    elif diff == -1:
        pass
    elif diff == -2:
        workout = decrement_workout(workout)
    elif diff == -3:
        workout = decrement_workout(workout, cycles=2)
    else:
        workout = decrement_workout(workout, cycles=len(workout.sets))

    db.update_workout_by_id(user_id, workout.id, workout)

    db.complete_set(user_id)

    return { "message" : SUCCESS }

@app.post("/workout/edit")
def edit_workout(auth_token: Annotated[str, Body()], workout: Workout):
    """
    Takes in an authtoken and the workout, updates the workout in the database to the new information.
    """
    user_id = db.check_auth_token(auth_token)
    if not user_id:
        return { "message" : AUTH_FAIL }
    
    if not db.get_workout_by_id(workout.id):
        return { "message" : NOT_FOUND }

    db.update_workout_by_id(user_id, workout.id, workout)

    return { "message" : SUCCESS }

@app.post("/workout/add")
def add_workout(auth_token: Annotated[str, Body()], workout: Workout):
    """
    Takes in an authtoken and the workout, adds the workout to the database.
    """
    user_id = db.check_auth_token(auth_token)
    if not user_id:
        return { "message" : AUTH_FAIL }
    
    db.add_workout(user_id, workout)

    return { "message" : SUCCESS }

@app.delete("/workout/delete")
def delete_workout(auth_token: Annotated[str, Body()], workout_id: Annotated[int, Body()]):
    """
    Takes in an authtoken and the workout id, deletes the workout in the database (has no effect of the id can't be found).
    """
    user_id = db.check_auth_token(auth_token)
    if not user_id:
        return { "message" : AUTH_FAIL }
    
    db.delete_workout_by_id(user_id, workout_id)

    return { "message" : SUCCESS }

@app.post("/split/edit")
def edit_split(auth_token: Annotated[str, Body()], split: Split):
    """
    Takes in an authtoken and the split, updates the split in the database to the new information.
    """
    user_id = db.check_auth_token(auth_token)
    if not user_id:
        return { "message" : AUTH_FAIL }
    
    if not db.get_day_by_name(user_id, split.name):
        return { "message" : NOT_FOUND }

    db.edit_day_by_name(user_id, split.name, split)

    return { "message" : SUCCESS }

@app.post("/split/add")
def add_workout(auth_token: Annotated[str, Body()], split: Split):
    """
    Takes in an authtoken and the split, adds the split to the database.
    """
    user_id = db.check_auth_token(auth_token)
    if not user_id:
        return { "message" : AUTH_FAIL }
    
    if not db.get_day_by_name(user_id, split.name):
        return { "message" : NOT_FOUND }
    
    db.add_day_to_plan(user_id, split.name)

    return { "message" : SUCCESS }

@app.delete("/split/delete")
def delete_workout(auth_token: Annotated[str, Body()], split_name: Annotated[int, Body()]):
    """
    Takes in an authtoken and the split name, deletes the split in the database (has no effect of the split can't be found).
    """
    user_id = db.check_auth_token(auth_token)
    if not user_id:
        return { "message" : AUTH_FAIL }
    
    db.delete_day_by_name(user_id, split_name)
    
    return { "message" : SUCCESS }

@app.put("/bulk/change")
def change_bulk(auth_token: Annotated[str, Body()]):
    """
    Takes in an authtoken, updates the bulk status in the database.
    """
    user_id = db.check_auth_token(auth_token)
    if not user_id:
        return { "message" : AUTH_FAIL }
    
    db.change_bulk_status(user_id)
    
    return { "message" : SUCCESS }

@app.get("/load")
def load_state(auth_token: Annotated[str, Body()]):
    # get current state
    """
            -- States --
        0    - 'inactive' Haven't started a workout 
        1    - 'active'   Workout started, in between selection
        2... - 'mid_set'  Current workout id + STATE_OFFSET
    """
    user_id = db.check_auth_token(auth_token)
    if not user_id:
        return { "message" : AUTH_FAIL }
    
    _state = db.get_state(user_id)

    results = LoadResult(state=_state)
    # if inactive, return state, current day, and list of workouts
    if _state == 'inactive' or _state == 'active':
        results.curr_day = db.get_current_day(user_id)
        results.all_workouts = db.get_all_workouts(user_id)

    # if active, return state, current day, and list of workouts, and completed list
    if _state == 'active':
        results.completed = db.get_completed_list(user_id)
 
    # if mid_set, return state, return current workout
    if _state == 'mid_set':
        results.workout = db.get_current_workout(user_id)

    return results