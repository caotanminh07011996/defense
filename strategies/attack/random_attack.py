import random
import math

class RandomAttackStrategy:
    def __init__(self, team, field):
        self.team = team
        self.field = field

    def apply(self):
        for robot in self.team.robots:
            if not getattr(robot, 'active', True):
                continue
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            norm = math.hypot(dx, dy)
            if norm == 0:
                continue
            dx /= norm
            dy /= norm
            step = 0.05
            new_x = robot.pose['x'] + dx * step
            new_y = robot.pose['y'] + dy * step

            if self.field.is_inside_field(new_x, new_y):
                robot.pose['x'] = new_x
                robot.pose['y'] = new_y
                robot.update()