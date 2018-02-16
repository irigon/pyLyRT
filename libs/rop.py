class Core:
    def __init__(self):
        self.roles={}

class Player(Core):
    def __init__(self):
        super().__init__()

    def type(self):
        return 'player'

class Role:
    def __init__(self):
        self.roles={}
    def type(self):
        return 'role'

class Compartment(Core):
    def __init__(self):
        super().__init__()

    def type(self):
        return 'compartment'
