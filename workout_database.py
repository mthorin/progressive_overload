import dataclasses
import secrets
import time

STATE_OFFSET = 2

@dataclasses.dataclass
class Workout:
    id: int
    sets: list[tuple[float, float]]
    name: str
    increment: int
    max_reps: int
    min_reps: int
    
@dataclasses.dataclass
class Day:
    name: str
    workouts: list[int]

@dataclasses.dataclass
class User:
    password: str
    state: int
    completed: list[bool]
    bulk: bool
    curr_day: int
    plan: list[Day]
    workouts: dict[Workout]
    next_workout_id: int

class WorkoutDatabase:
    def __init__(self):
        self.user_data = dict()
        self.auth = dict()

    def generate_auth(self, user_id: str):
        authtoken = secrets.token_urlsafe(16)
        self.auth[authtoken] = (user_id, time.time())
        return authtoken

    def log_in_user(self, user_id: str, password: str):
        data = self.user_data.get(user_id)

        if data == None:
            return None
        
        if data.password != password:
            return None

        return self.generate_auth(user_id)

    def log_out_user(self, auth_token: str):
        self.auth.pop(auth_token, default = None)

    def create_user(self, user_id: str, password: str):
        if self.user_data.get(user_id):
            return None
        
        self.user_data[user_id] = User(
            password, 
            0, 
            [], 
            True, 
            0, 
            [], 
            dict(), 
            1)

        return self.generate_auth(user_id)

    def check_auth_token(self, auth_token: str):
        auth_data = self.auth.get(auth_token, default = None)

        if auth_data == None:
            return False
        
        if time.time() - auth_data[1] > 1800:
            self.auth.pop(auth_token)
            return False
        
        self.auth[auth_token] = (auth_data[0], time.time())

        return True
    
    """
            -- States --
        0    - 'inactive' Haven't started a workout 
        1    - 'active'   Workout started, in between selection
        2... - 'mid_set'  Current workout id + STATE_OFFSET
    """

    def get_state(self, user_id: str):
        state = self.user_data[user_id].state
        if state > 1:
            return 'mid_set'
        if state == 1:
            return 'active'
        return 'inactive'
    
    def check_bulk_status(self, user_id: str):
        return self.user_data[user_id].bulk
    
    def initiate_workout(self, user_id: str):
        self.user_data[user_id].state = 1

        day = self.user_data[user_id].plan[self.user_data[user_id].curr_day]

        self.user_data[user_id].completed = [False] * len(day.workouts)

    def get_current_workout(self, user_id: str):
        data = self.user_data[user_id]
        state = data.state
        day = data.plan[data.curr_day]

        workout_id = day.workouts[state - STATE_OFFSET]
        return data.workouts[workout_id]

    def update_workout_by_id(self, user_id: str, workout_id: int, new_workout: Workout):
        self.user_data[user_id].workouts[workout_id] = new_workout

    def get_workout_by_id(self, user_id: str, workout_id: int):
        return self.user_data[user_id].workouts[workout_id]
    
    def add_workout(self, user_id: str, new_workout: Workout):
        new_workout.id = self.user_data[user_id].next_workout_id
        self.user_data[user_id].next_workout_id += 1
        self.user_data[user_id].workouts[new_workout.id] = new_workout

    def delete_workout(self, user_id: str, workout_id: int):
        self.user_data[user_id].workouts.pop(workout_id)

    def complete_set(self, user_id: str):
        state = self.user_data[user_id].state
        self.user_data[user_id].completed[state - STATE_OFFSET] = True
        self.user_data[user_id].state = 1