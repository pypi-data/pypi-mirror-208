class Bar:
    def __init__(self, exec = '', params = {}):
        self.exec = exec
        self.params = params

    def get(self):
        cmd = ["bar {"]

        cmd.append(f'\tstatus_command {self.exec} \\')

        keys = list(self.params.keys())

        length = len(keys) - 1

        for i in range(length):
            name = keys[i]
            args = ' '.join(self.params[name])

            cmd.append(f'\t\t{name} {args} \\')

        
        name = keys[length]
        args = ' '.join(self.params[name])

        cmd.append(f'\t\t{name} {args}')

        cmd.append('}')
        return '\n'.join(cmd)
