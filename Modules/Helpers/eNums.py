from enum import Enum


class RuningState(Enum):
    NOTINITIALIZED =0
    INITIALIZED=1
    STARTED =2
    RUNNING=3
    STOPPED=4
