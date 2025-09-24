import dataclasses

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

    