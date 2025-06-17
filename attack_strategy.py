import math

class AttackStrategy:
    def __init__(self, team2, team1, target_point, scale, field, controlled_robots, attack_speed=1.0):
        self.team2 = team2
        self.team1 = team1
        self.target_point = target_point
        self.scale = scale
        self.field = field
        self.controlled_robots = controlled_robots
        self.attack_speed = attack_speed

    def update(self, is_running):
        if not is_running:
            return

        target_x, target_y = self.target_point
        Ka = 1.0
        Kr = 2.0
        safe_distance = 1.0
        step_size = self.attack_speed * 0.05

        for robot in self.team2.robots:
            if robot in self.controlled_robots:
                continue

            rx = robot.pose['x']
            ry = robot.pose['y']
            dx = target_x - rx
            dy = target_y - ry
            distance_to_target = math.hypot(dx, dy)
            if distance_to_target < 0.1:
                continue

            fx = Ka * dx / distance_to_target
            fy = Ka * dy / distance_to_target

            all_robots = self.team1.robots + self.team2.robots
            for other in all_robots:
                if other == robot:
                    continue
                ox, oy = other.pose['x'], other.pose['y']
                dxo = rx - ox
                dyo = ry - oy
                dist = math.hypot(dxo, dyo)
                if dist < safe_distance and dist > 0.05:
                    repulse = Kr / (dist ** 2)
                    fx += repulse * (dxo / dist)
                    fy += repulse * (dyo / dist)

            total_force = math.hypot(fx, fy)
            if total_force > 0:
                fx = fx / total_force
                fy = fy / total_force

            move_dist = min(step_size, distance_to_target)
            vx = move_dist * fx
            vy = move_dist * fy

            new_x = robot.pos().x() + vx * self.scale
            new_y = robot.pos().y() + vy * self.scale

            x_m = (new_x + self.team2.robot_size / 2 - self.field.MARGIN) / self.scale - 11.0
            y_m = (new_y + self.team2.robot_size / 2 - self.field.MARGIN) / self.scale - 7.0

            if self.is_inside_field(x_m, y_m):
                robot.setPos(new_x, new_y)
                robot.pose['x'] = x_m
                robot.pose['y'] = y_m

            desired_theta = math.degrees(math.atan2(fy, fx)) % 360
            robot.setRotation(desired_theta)
            robot.pose['theta'] = desired_theta

    def is_inside_field(self, x, y):
        return -12.0 <= x <= 12.0 and -8.0 <= y <= 8.0
