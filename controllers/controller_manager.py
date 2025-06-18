# controllers/controller_manager.py

from controllers.xbox_controller import assign_xbox_controllers
from strategies.defense.random_defense import RandomDefenseStrategy
from strategies.attack.random_attack import RandomAttackStrategy

def ControllerManager(team, mode, strategy_name, side=None, field=None):
    controllers = []
    auto_robots = []

    if mode == "Xbox":
        controllers, auto_robots = assign_xbox_controllers(team)
    else:
        auto_robots = team.robots

    strategy = None
    if strategy_name == "Random":
        if side == 'defense':
            from strategies.defense.random_defense import RandomDefenseStrategy
            strategy = RandomDefenseStrategy(team, field)
        elif side == 'attack':
            from strategies.attack.random_attack import RandomAttackStrategy
            strategy = RandomAttackStrategy(team, field)

    return controllers, auto_robots, strategy
