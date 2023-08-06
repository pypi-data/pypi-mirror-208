from util.util import Util

from i3.cmd import Cmd, ExecCmd

Mod = 'Mod4'
Ctrl = 'Ctrl'
Shift = 'Shift'


class Key:
    def __init__(self, modifier = [], key = '', cmd = {}, desc = '', mod = True):
        self.modifier = modifier
        self.key = f'{key}'
        if 'ext' in cmd and cmd['ext']:
            del cmd['ext']
            self.cmd = ExecCmd(**cmd)
        else:
            self.cmd = Cmd(**cmd)
        self.desc = desc
        self.mod = Util.to_bool(mod)

    def getModifier(self):
        modifier = []
        
        if self.mod:
            modifier.append('$mod')

        modifier.extend(self.modifier)

        return modifier

    def getKeyAsStr(self):
        keyStr = ''

        if len(self.getModifier()) > 0:
            keyStr = '+'.join(self.getModifier())

        keyStr = self.key if keyStr == '' else f'{keyStr}+{self.key}'

        return keyStr

    def getKeybinding(self, prepend = ''):
        keys = self.getModifier()
        keys.append(self.key)

        keysStr = '+'.join(keys)

        return [f'{prepend}# {self.desc}', f'{prepend}bindsym {self.getKeyAsStr()} {self.cmd.getCmd()}']

    def getKeymapDesc(self):
        return f'{self.getKeyAsStr()}: {self.desc}'


def setMod():
    return f'set $mod {Mod}'
