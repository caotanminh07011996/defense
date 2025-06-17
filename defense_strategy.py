import math
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtGui import QBrush, QPen, QColor
from PyQt5.QtCore import Qt

class DefenseStrategy:
    def __init__(self, team_blue, team_red, target_point, field, scale):
        self.team_blue = team_blue
        self.team_red = team_red
        self.target_point = target_point  # (x, y)
        self.field = field
        self.scene = team_blue.scene
        self.SCALE = scale

        self.speed = 0.5         # m/s
        self.rotate_speed = 5.0    # deg/s
        self.dt = 0.05             # 50ms
        self.intercept_items = []

    def is_inside_field(self, x, y):
        return -12.0 <= x <= 12.0 and -8.0 <= y <= 8.0

    def is_position_free(self, x, y, current_robot, min_dist=0.7):
        all_robots = self.team_blue.robots + self.team_red.robots
        for robot in all_robots:
            if robot is current_robot:
                continue
            dist = math.hypot(x - robot.pose['x'], y - robot.pose['y'])
            if dist < min_dist:
                return False
        return True

    def get_intercept_point(self, red_pos, blue_pos):
        rx, ry = red_pos
        tx, ty = self.target_point
        bx, by = blue_pos

        dx = tx - rx
        dy = ty - ry
        if dx == 0 and dy == 0:
            return rx, ry

        t = ((bx - rx) * dx + (by - ry) * dy) / (dx**2 + dy**2)
        t = max(0.0, min(1.0, t))
        return rx + t * dx, ry + t * dy

    def draw_intercept_point(self, x, y):
        r = 0.1 * self.SCALE
        cx = self.field.MARGIN + (x + 11.0) * self.SCALE
        cy = self.field.MARGIN + (y + 7.0) * self.SCALE
        ellipse = QGraphicsEllipseItem(cx - r, cy - r, 2 * r, 2 * r)
        ellipse.setBrush(QBrush(QColor("yellow")))
        ellipse.setPen(QPen(Qt.NoPen))
        self.scene.addItem(ellipse)
        self.intercept_items.append(ellipse)

    def update(self):
        red_robots = self.team_red.robots
        blue_robots = self.team_blue.robots
        assigned = min(len(red_robots), len(blue_robots))

        # Xóa điểm intercept cũ
        for item in self.intercept_items:
            self.scene.removeItem(item)
        self.intercept_items.clear()

        for i in range(assigned):
            red = red_robots[i]
            blue = blue_robots[i]

            red_pos = (red.pose['x'], red.pose['y'])
            blue_pos = (blue.pose['x'], blue.pose['y'])
            tx, ty = self.get_intercept_point(red_pos, blue_pos)

            self.draw_intercept_point(tx, ty)

            dx = tx - blue_pos[0]
            dy = ty - blue_pos[1]
            dist = math.hypot(dx, dy)

            desired_theta = math.degrees(math.atan2(dy, dx)) % 360
            current_theta = blue.pose['theta']
            dtheta = (desired_theta - current_theta + 540) % 360 - 180

            if dist > 0.05:
                print(f"[DEFENSE] Robot {i}: dist to intercept = {dist:.3f}")
                move_dist = min(self.speed * self.dt, dist)
                vx = move_dist * dx / dist
                vy = move_dist * dy / dist

                new_x = blue.pos().x() + vx * self.SCALE
                new_y = blue.pos().y() + vy * self.SCALE

                x_m = (new_x + self.team_blue.robot_size / 2 - self.field.MARGIN) / self.SCALE - 11.0
                y_m = (new_y + self.team_blue.robot_size / 2 - self.field.MARGIN) / self.SCALE - 7.0

                if self.is_inside_field(x_m, y_m) and self.is_position_free(x_m, y_m, blue):
                    blue.setPos(new_x, new_y)
                    blue.pose['x'] = x_m
                    blue.pose['y'] = y_m

            if abs(dtheta) > 1.0:
                delta = math.copysign(min(abs(dtheta), self.rotate_speed * self.dt), dtheta)
                new_theta = (current_theta + delta) % 360
                blue.setRotation(new_theta)
                blue.pose['theta'] = new_theta
    def clear_intercepts(self):
        for item in self.intercept_items:
            self.scene.removeItem(item)
        self.intercept_items.clear()
