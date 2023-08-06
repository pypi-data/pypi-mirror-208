
class Manager():
    self.update = []
    self.draw = []

    def __init__(self):
        pass

    def add_update(self, func):
        self.update.append(func)
        return func

    def add_draw(self, func):
        self.draw.append(func)
        return func

    def run_update(self):
        for func in self.update:
            func()

    def run_draw(self):
        for func in self.draw:
            func()