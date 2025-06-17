import sys
import math
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QFileDialog
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import QPainter
from PyQt5 import uic

from models.field import Field
from models.team import Team
from defense_strategy import DefenseStrategy
from recorder import Recorder, Replayer
from config import SCALE, ROBOT_SIZE

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/Interface2.ui", self)

        self.SCALE = SCALE
        self.setup_scene()

        self.field = Field(self.SCALE)
        self.field.draw(self.scene)
        self.graphicsView.fitInView(QRectF(0, 0, *self.field.get_dimensions()), Qt.KeepAspectRatio)

        self.team1 = Team(1, Qt.blue, self.field.MARGIN, self.scene)
        positions_blue = [(5.5, 2, 180), (7, -2, 180), (8, -1.5, 180), (9, -3, 0), (10, -3.5, 180)]
        self.team1.create_robots(len(positions_blue), positions=positions_blue)

        self.team2 = Team(2, Qt.red, self.field.MARGIN, self.scene)
        #positions_red = [(-7, 0, 180), (-7, 2, 180), (-7, 4, 180), (-7, -2, 180), (-7, -4, 180)]
        positions_red = [(-7, 0, 180)]
        self.team2.create_robots(len(positions_red), positions=positions_red)

        self.recorder = Recorder(self.team1, self.team2)
        self.replayer = Replayer(self.scene, self.team1, self.team2,
                                  scale=self.SCALE, margin=self.field.MARGIN, robot_size=self.team1.robot_size)
        self.pushButton_Save.clicked.connect(self.toggle_recording)
        self.pushButton_Replay.clicked.connect(self.load_replay_file)
        self.pushButton_Reset.clicked.connect(self.reset_game)

        self.target_point = (11.0, 0.0)

        self.defense_strategy = DefenseStrategy(self.team1, self.team2, self.target_point, self.field, self.SCALE)
        self.defense_timer = QTimer()
        self.defense_timer.timeout.connect(self.defense_strategy.update)
        self.defense_timer.start(50)

        # Xbox logic
        pygame.init()
        pygame.joystick.init()
        self.controllers = []
        self.controlled_robots = []
        self.setup_xbox_controllers()

        self.xbox_timer = QTimer()
        self.xbox_timer.timeout.connect(self.poll_xbox_inputs)
        self.xbox_timer.start(50)

        # Auto attack cho các robot đỏ chưa được điều khiển
        self.attack_speed = 1.0  # m/s
        self.attack_timer = QTimer()
        self.attack_timer.timeout.connect(self.update_red_team_attack)
        self.attack_timer.start(50)

    def setup_scene(self):
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.graphicsView.setRenderHint(QPainter.SmoothPixmapTransform)
        self.graphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsView.setAlignment(Qt.AlignCenter)

    def setup_xbox_controllers(self):
        self.controllers.clear()
        self.controlled_robots.clear()

        pygame.joystick.quit()
        pygame.joystick.init()
        num_joysticks = pygame.joystick.get_count()

        print(f"Phát hiện {num_joysticks} Xbox controllers")

        for i, robot in enumerate(self.team2.robots):
            if i < num_joysticks:
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                self.controllers.append((robot, joystick))
                self.controlled_robots.append(robot)
    def poll_xbox_inputs(self):
        pygame.event.pump()
        DEAD_ZONE = 0.05
        MOVE_SPEED = 2.0
        ROTATE_SPEED = 10.0
        safe_distance = 1.0
        dt = 0.05

        for robot, joystick in self.controllers:
            lx = joystick.get_axis(0)
            ly = -joystick.get_axis(1)
            rx = joystick.get_axis(3)

            if abs(lx) < DEAD_ZONE: lx = 0
            if abs(ly) < DEAD_ZONE: ly = 0
            if abs(rx) < DEAD_ZONE: rx = 0

            dx = lx * MOVE_SPEED * dt
            dy = ly * MOVE_SPEED * dt

            # Dự đoán vị trí mới nếu move toàn bộ
            pos = robot.pos()
            x_m = (pos.x() + dx * self.SCALE + self.team2.robot_size / 2 - self.field.MARGIN) / self.SCALE - 11.0
            y_m = (pos.y() - dy * self.SCALE + self.team2.robot_size / 2 - self.field.MARGIN) / self.SCALE - 7.0

            # Kiểm tra va chạm và loại bỏ thành phần vận tốc va chạm
            for other in self.team2.robots + self.team1.robots:
                if other == robot:
                    continue

                ox, oy = other.pose['x'], other.pose['y']
                diff_x = ox - robot.pose['x']
                diff_y = oy - robot.pose['y']
                dist = math.hypot(diff_x, diff_y)

                if dist < safe_distance and dist > 0.05:
                    # Chuẩn hóa vector hướng về vật cản
                    ux = diff_x / dist
                    uy = diff_y / dist

                    # Dự phóng vận tốc lên hướng vật cản
                    projection = dx * ux + dy * uy
                    if projection > 0:  # Chỉ chặn nếu đang đi về phía vật cản
                        dx -= projection * ux
                        dy -= projection * uy

            # Sau khi xử lý tránh va chạm
            new_x = pos.x() + dx * self.SCALE
            new_y = pos.y() - dy * self.SCALE

            x_m = (new_x + self.team2.robot_size / 2 - self.field.MARGIN) / self.SCALE - 11.0
            y_m = (new_y + self.team2.robot_size / 2 - self.field.MARGIN) / self.SCALE - 7.0

            if self.is_inside_field(x_m, y_m):
                robot.setPos(new_x, new_y)
                robot.pose['x'] = x_m
                robot.pose['y'] = y_m

            # Quay như cũ
            if rx != 0:
                theta = (robot.rotation() + ROTATE_SPEED * rx * dt) % 360
                robot.setRotation(theta)
                robot.pose['theta'] = theta
                
    '''
    def poll_xbox_inputs(self):
        pygame.event.pump()
        DEAD_ZONE = 0.05
        MOVE_SPEED = 2.0
        ROTATE_SPEED = 10.0
        safe_distance = 1.0
        dt = 0.05

        for robot, joystick in self.controllers:
            lx = joystick.get_axis(0)
            ly = -joystick.get_axis(1)
            rx = joystick.get_axis(3)

            if abs(lx) < DEAD_ZONE: lx = 0
            if abs(ly) < DEAD_ZONE: ly = 0
            if abs(rx) < DEAD_ZONE: rx = 0

            dx = lx * MOVE_SPEED * dt
            dy = ly * MOVE_SPEED * dt

            pos = robot.pos()
            new_x = pos.x() + dx * self.SCALE
            new_y = pos.y() - dy * self.SCALE

            x_m = (new_x + self.team2.robot_size / 2 - self.field.MARGIN) / self.SCALE - 11.0
            y_m = (new_y + self.team2.robot_size / 2 - self.field.MARGIN) / self.SCALE - 7.0

            blocked = False

            for other in self.team2.robots + self.team1.robots:
                if other == robot:
                    continue
                ox, oy = other.pose['x'], other.pose['y']
                dist = math.hypot(x_m - ox, y_m - oy)
                if dist < safe_distance:
                    blocked = True
                    break

            # Nếu có va chạm trên hướng tịnh tiến, chỉ cho phép quay, không cho phép move
            if blocked:
                dx = 0
                dy = 0
                x_m = robot.pose['x']
                y_m = robot.pose['y']
                new_x = (x_m + 11.0) * self.SCALE - self.team2.robot_size / 2 + self.field.MARGIN
                new_y = (y_m + 7.0) * self.SCALE - self.team2.robot_size / 2 + self.field.MARGIN

            if self.is_inside_field(x_m, y_m):
                robot.setPos(new_x, new_y)
                robot.pose['x'] = x_m
                robot.pose['y'] = y_m

            # Quay như cũ
            if rx != 0:
                theta = (robot.rotation() + ROTATE_SPEED * rx * dt) % 360
                robot.setRotation(theta)
                robot.pose['theta'] = theta
    '''
    def update_red_team_attack(self):
        target_x, target_y = self.target_point
        Ka = 1.0
        Kr = 2.0
        safe_distance = 1.0
        step_size = self.attack_speed * 0.05

        for robot in self.team2.robots:
            if robot in self.controlled_robots:
                continue

            rx, ry = robot.pose['x'], robot.pose['y']
            dx = target_x - rx
            dy = target_y - ry
            distance_to_target = math.hypot(dx, dy)
            if distance_to_target < 0.1:
                continue

            fx = Ka * dx / distance_to_target
            fy = Ka * dy / distance_to_target

            for other in self.team1.robots + self.team2.robots:
                if other == robot:
                    continue
                ox, oy = other.pose['x'], other.pose['y']
                dxo = rx - ox
                dyo = ry - oy
                dist = math.hypot(dxo, dyo)
                if dist < safe_distance and dist > 0.05:
                    repulse = Kr / (dist**2)
                    fx += repulse * (dxo / dist)
                    fy += repulse * (dyo / dist)

            total_force = math.hypot(fx, fy)
            if total_force > 0:
                fx, fy = fx / total_force, fy / total_force

            move_dist = min(step_size, distance_to_target)
            vx = move_dist * fx
            vy = move_dist * fy

            new_x = robot.pos().x() + vx * self.SCALE
            new_y = robot.pos().y() + vy * self.SCALE

            x_m = (new_x + self.team2.robot_size / 2 - self.field.MARGIN) / self.SCALE - 11.0
            y_m = (new_y + self.team2.robot_size / 2 - self.field.MARGIN) / self.SCALE - 7.0

            if self.is_inside_field(x_m, y_m):
                robot.setPos(new_x, new_y)
                robot.pose['x'] = x_m
                robot.pose['y'] = y_m

            desired_theta = math.degrees(math.atan2(fy, fx)) % 360
            robot.setRotation(desired_theta)
            robot.pose['theta'] = desired_theta

    def is_inside_field(self, x, y):
        return -12.0 <= x <= 12.0 and -8.0 <= y <= 8.0

    def toggle_recording(self):
        if not self.recorder.saving:
            self.recorder.start()
            self.pushButton_Save.setText("Saving...")
        else:
            self.recorder.stop()
            self.pushButton_Save.setText("Save")

    def load_replay_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file replay", "data", "CSV Files (*.csv)")
        if not file_path:
            return
        self.replayer.load_csv(file_path)
        self.replayer.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.graphicsView.fitInView(QRectF(0, 0, *self.field.get_dimensions()), Qt.KeepAspectRatio)

    def reset_game(self):
        # Dừng các timer trước khi reset
        self.defense_timer.stop()
        self.attack_timer.stop()
        self.xbox_timer.stop()

        # Clear các intercept cũ trên scene
        if hasattr(self, 'defense_strategy'):
            self.defense_strategy.clear_intercepts()

        # Xóa robot cũ
        self.team1.clear_robots()
        self.team2.clear_robots()
        self.controllers.clear()
        self.controlled_robots.clear()

        # Tạo lại robot mới
        positions_blue = [(5.5, 2, 180), (7, -2, 180), (8, -1.5, 180), (9, -3, 0), (10, -3.5, 180)]
        self.team1.create_robots(len(positions_blue), positions=positions_blue)

        #positions_red = [(-7, 0, 180), (-7, 2, 180), (-7, 4, 180), (-7, -2, 180), (-7, -4, 180)]
        positions_red = [(-7, 0, 180)]
        self.team2.create_robots(len(positions_red), positions=positions_red)

        # Gán lại Xbox cho robot đỏ mới
        self.setup_xbox_controllers()

        # Quan trọng: Khởi tạo lại chiến thuật phòng thủ với robot mới
        self.defense_strategy = DefenseStrategy(self.team1, self.team2, self.target_point, self.field, self.SCALE)
        self.defense_timer.timeout.disconnect()
        self.defense_timer.timeout.connect(self.defense_strategy.update)

        # Khởi động lại timer
        self.defense_timer.start(50)
        self.attack_timer.start(50)
        self.xbox_timer.start(50)
                

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
