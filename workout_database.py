import dataclasses
import secrets
import time

@dataclasses.dataclass
class Workout:
    sets: list[tuple[int, int]]
    name: str
    increment: int
    max_reps: int
    min_reps: int
    
@dataclasses.dataclass
class Day:
    workouts: list[Workout]

@dataclasses.dataclass
class Plan:
    days: list[Day]

@dataclasses.dataclass
class User:
    password: str
    state: int
    completed: list[bool]
    bulk: bool
    curr_day: int
    plan: Plan

# -- States --
# 0 - Haven't started a workout
# 1 - Workout started, in between selection
# 2... - Current workout

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
        
        self.user_data[user_id] = User(password, 0, [], True, 0, Plan([]))

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

    def get_state(self, user_id: str):
        pass

    def get_current_workout(self, user_id: str):
        pass

    def initiate_workout(self, user_id: str):
        pass

    def update_workout_by_id(self, workout_id: str, new_workout: Workout):
        pass

    def complete_set(self, user_id: str):
        pass