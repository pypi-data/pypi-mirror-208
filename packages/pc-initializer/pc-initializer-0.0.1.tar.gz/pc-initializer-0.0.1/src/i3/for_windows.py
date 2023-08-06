class ForWindows:
    def __init__(self, condition, command):
        self.condition = condition
        self.command = command

    def getCommand(self):
        conditions = []
        for attribute in self.condition:
            conditions.append(f'{attribute}="{self.condition[attribute]}"')

        return f"for_window [{' '.join(conditions)}] {self.command}"

# get class with xprop 
