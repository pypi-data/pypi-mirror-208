import sys
sys.path.insert(1, '/wsp/github/linux-setup')
from util.util import Util

class Cmd:
    def __init__(self, cmd = ''):
        self.cmd = cmd

    def getCmd(self):
        return f'{self.cmd}'

class ExecCmd(Cmd):
    def __init__(self, cmd = '', no_startup_id = True, always = False):
        self.cmd = cmd
        self.no_startup_id = Util.to_bool(no_startup_id)
        self.always = Util.to_bool(always)

    def getCmd(self):
        exec = 'exec_always' if self.always else 'exec'
        startup = '--no-startup-id' if self.no_startup_id else ''
        return f'{exec} {startup} {self.cmd}'
