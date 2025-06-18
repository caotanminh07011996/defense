from strategies.attack.random_attack import RandomAttackStrategy
from strategies.defense.random_defense import RandomDefenseStrategy

class StrategyManager:
    def __init__(self, team_blue, team_red, field):
        self.team_blue = team_blue
        self.team_red = team_red
        self.field = field

        self.attack_strategy = RandomAttackStrategy(self.team_red, self.field)
        self.defense_strategy = RandomDefenseStrategy(self.team_blue, self.field)

    def set_attack_strategy(self, strategy_class):
        self.attack_strategy = strategy_class(self.team_red, self.field)

    def set_defense_strategy(self, strategy_class):
        self.defense_strategy = strategy_class(self.team_blue, self.field)

    def apply_strategies(self):
        self.attack_strategy.apply()
        self.defense_strategy.apply()
