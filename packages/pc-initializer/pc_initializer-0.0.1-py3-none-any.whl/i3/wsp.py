from i3.key import Key, Ctrl, Shift
from i3.cmd import Cmd

class Workspace:
    def __init__(self, key, name = None, applications = []):
        self.key = key
        self.name = name if name != None else self.key
        self.applications = applications

        switch = {
            "key": key, 
            "cmd": {
                "cmd": f'workspace {self.name}'
            },
            "desc": f'Switch to ws {self.name}'
        }
        self.switch = Key(**switch)

        move = {
            "modifier": ["Ctrl"], 
            "key": key, 
            "cmd": {
                "cmd": f'move container to workspace {self.name}'
            },
            "desc": f'Move container to ws {self.name}'
        }
        self.move = Key(**move)

        move_and_switch = {
            "modifier": ["Shift"], 
            "key": key, 
            "cmd": {
                "cmd": f'move container to workspace {self.name}; workspace {self.name}'
            },
            "desc": f'Move container and switch to ws {self.name}'
        }
        self.move_and_switch = Key(**move_and_switch)

    def getKeys(self):
        key_bindings = []

        for k in [self.switch, self.move, self.move_and_switch]:
            key_bindings.append(k)

        return key_bindings

    def getAssignCmds(self):
        assignCmds = []

        for application in self.applications:
           assignCmds.append(f'assign [class="{application}"] {self.name}')

        return assignCmds
