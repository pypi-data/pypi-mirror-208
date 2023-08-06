class Machine:
    def __init__(self, name):
        self.name = name

    def run(self, data):
        return data

    def __repr__(self):
        return f"Machine(name={self.name})"