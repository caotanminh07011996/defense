class BaseAttackStrategy:
    def __init__(self, team, field):
        self.team = team
        self.field = field

    def apply(self):
        raise NotImplementedError("Attack strategy must implement apply()")
