from typing import List, Optional

from pydantic import BaseModel


class Action(BaseModel):
    action_name: str

    # which path you want run commands
    path: str
    commands: List[str]

    # time out how many long a process
    timeout: Optional[float] = None


class Setting(BaseModel):
    # Show one Top and process bar
    name: str

    # enable or disable debug
    debug: Optional[bool] = False

    # setUp log file path
    # default not saves log
    logfile: Optional[str] = ""

    # list of action and commands
    actions: List[Action]
