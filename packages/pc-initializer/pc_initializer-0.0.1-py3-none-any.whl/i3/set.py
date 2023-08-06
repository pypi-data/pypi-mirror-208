class Set:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def get(self):
        return f'set {self.name} {self.value}'

class SetFromResource:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def get(self):
        return f'set_from_resource {self.name} {self.value}'
