from i3.key import Key
from i3.cmd import ExecCmd, Cmd
from i3.set import Set

class Mode:
    def __init__(self, name = '', modifier = [], key = '', options = []):
        self.name = name
        self.modifier = modifier
        self.key = key

        self.start = {
            "modifier": modifier,
            "key": key,
            "cmd": {
                "cmd": f'mode "{name}"'
            },
            "desc": f'Start {name} mode'
        }

        option_help = []

        self.options = []

        for option in options:
            self.options.append(Key(**option))

        
        for k in ['Return', 'Escape']:
            self.options.append(Key(**
                {
                    "key": k, 
                    "mod": False,
                    "cmd": {
                        "cmd": "mode \"default\""
                    },
                    "desc": "Cancel" 
                }
            ))


    def getStart(self):
        return Key(**self.start)

    def getModeConfig(self):
        start = self.getStart()
        mode = start.getKeybinding()

        option_help = []
        for option in self.options:
            option_help.append(
                f'[{option.getKeyAsStr()}] {option.desc}'
            )

        mode.append(Set(self.name, ', '.join(option_help)).get())

        mode.append(f'mode "{self.name}" {{')

        for option in self.options:
            keyBinding = option.getKeybinding('\t')

            mode.extend(keyBinding)

        mode.append('}')

        return mode

