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
from controllers.controller_manager import ControllerManager  # Giữ nguyên

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/Interface.ui", self)

        self.SCALE = SCALE
        self.setup_scene()

        self.field = Field(self.SCALE)
        self.field.draw(self.scene)
        self.graphicsView.fitInView(QRectF(0, 0, *self.field.get_dimensions()), Qt.KeepAspectRatio)

        self.team1 = Team(1, Qt.blue, self.field.MARGIN, self.scene)
        self.team2 = Team(2, Qt.red, self.field.MARGIN, self.scene)

        positions_blue = [(6, 1, 180), (6, -1, 180), (6, 2, 180), (6, -3, 180), (6, -7, 180)]
        self.team1.create_robots(len(positions_blue), positions=positions_blue)

        positions_red = [(-7, 0, 180), (-7, 2, 180), (-7, 4, 180), (-7, -2, 180), (-7, -4, 180)]
        self.team2.create_robots(len(positions_red), positions=positions_red)

        self.recorder = Recorder(self.team1, self.team2)
        self.replayer = Replayer(self.scene, self.team1, self.team2,
                                  scale=self.SCALE, margin=self.field.MARGIN, robot_size=self.team1.robot_size)

        self.pushButton_Save.clicked.connect(self.toggle_recording)
        self.pushButton_Replay.clicked.connect(self.load_replay_file)
        self.pushButton_Reset.clicked.connect(self.reset_game)
        self.pushButton_Start.clicked.connect(self.start_game)

        # Logic mới: Control Manager cho mỗi team
        self.team1_controllers = []
        self.team1_auto_robots = []
        self.team2_controllers = []
        self.team2_auto_robots = []

        pygame.init()
        pygame.joystick.init()

        self.is_running = False
        self.game_state = "stopped"

        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(50)

    def setup_scene(self):
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.graphicsView.setRenderHint(QPainter.SmoothPixmapTransform)
        self.graphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsView.setAlignment(Qt.AlignCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.graphicsView.fitInView(QRectF(0, 0, *self.field.get_dimensions()), Qt.KeepAspectRatio)

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

    def reset_game(self):
        self.team1.clear_robots()
        self.team2.clear_robots()

        positions_blue = [(6, 1, 180), (6, -1, 180), (6, 2, 180), (6, -3, 180), (6, -7, 180)]
        self.team1.create_robots(len(positions_blue), positions=positions_blue)

        positions_red = [(-7, 0, 180), (-7, 2, 180), (-7, 4, 180), (-7, -2, 180), (-7, -4, 180)]
        self.team2.create_robots(len(positions_red), positions=positions_red)

        self.setup_controls()

    def start_game(self):
        if self.game_state == "stopped":
            self.game_state = "running"
            self.is_running = True
            self.labelGameState.setText("Game Running...")
            self.pushButton_Start.setText("Pause")
            self.setup_controls()  # Khởi tạo điều khiển khi bắt đầu
        elif self.game_state == "running":
            self.game_state = "paused"
            self.is_running = False
            self.labelGameState.setText("Game Pause...")
            self.pushButton_Start.setText("Continue")
        elif self.game_state == "paused":
            self.game_state = "running"
            self.is_running = True
            self.labelGameState.setText("Game Running...")
            self.pushButton_Start.setText("Pause")

    def setup_controls(self):
        from controllers.controller_manager import ControllerManager
        # Lấy mode và strategy từ UI
        mode1 = self.comboBox_ModeBlue.currentText()
        strat1 = self.comboBox_StrategyBlue.currentText()
        mode2 = self.comboBox_ModeRed.currentText()
        strat2 = self.comboBox_StrategyRed.currentText()

        self.team1_controllers, self.team1_auto_robots, self.team1_strategy = ControllerManager.setup_control(self.team1, mode1, strat1)
        self.team2_controllers, self.team2_auto_robots, self.team2_strategy = ControllerManager.setup_control(self.team2, mode2, strat2)

    def game_loop(self):
        if not self.is_running:
            return

        pygame.event.pump()

        for robot, joystick in self.team1_controllers:
            self.poll_xbox_single(robot, joystick)

        for robot, joystick in self.team2_controllers:
            self.poll_xbox_single(robot, joystick)

        for robot in self.team1_auto_robots:
            self.apply_strategy(robot, self.team1_strategy)

        for robot in self.team2_auto_robots:
            self.apply_strategy(robot, self.team2_strategy)

        self.check_game_state()

    def poll_xbox_single(self, robot, joystick):
        DEAD_ZONE = 0.05
        MOVE_SPEED = 2.0
        ROTATE_SPEED = 10.0

        lx = joystick.get_axis(0)
        ly = -joystick.get_axis(1)
        rx = joystick.get_axis(3)

        if abs(lx) < DEAD_ZONE: lx = 0
        if abs(ly) < DEAD_ZONE: ly = 0
        if abs(rx) < DEAD_ZONE: rx = 0

        dx = lx * MOVE_SPEED * 0.05
        dy = ly * MOVE_SPEED * 0.05

        pos = robot.pos()
        new_x = pos.x() + dx * self.SCALE
        new_y = pos.y() - dy * self.SCALE

        x_m = (new_x + ROBOT_SIZE / 2 - self.field.MARGIN) / self.SCALE - 11.0
        y_m = (new_y + ROBOT_SIZE / 2 - self.field.MARGIN) / self.SCALE - 7.0

        # Thêm kiểm tra tránh va chạm
        safe = True
        all_robots = self.team1.robots + self.team2.robots

        for other in all_robots:
            if other == robot:
                continue
            ox = other.pose['x']
            oy = other.pose['y']

            dist_to_other = math.hypot(x_m - ox, y_m - oy)
            min_safe_distance = (ROBOT_SIZE / self.SCALE) + 0.1

            if dist_to_other < min_safe_distance:
                safe = False
                break

        if safe and self.is_inside_field(x_m, y_m):
            robot.setPos(new_x, new_y)
            robot.pose['x'] = x_m
            robot.pose['y'] = y_m

        if rx != 0:
            theta = (robot.rotation() + ROTATE_SPEED * rx * 0.05) % 360
            robot.setRotation(theta)
            robot.pose['theta'] = theta

    def apply_strategy(self, robot, strategy):
        if strategy == 'Straight':
            tx, ty = self.field.target_zone.cx, self.field.target_zone.cy
            dx = tx - robot.pose['x']
            dy = ty - robot.pose['y']
            dist_to_target = math.hypot(dx, dy)

            if dist_to_target > 0.1:

                # Bước 1: hướng di chuyển cơ bản
                vx = 0.05 * dx / dist_to_target
                vy = 0.05 * dy / dist_to_target

                # Bước 2: kiểm tra tránh va chạm với các robot khác
                safe = True
                all_robots = self.team1.robots + self.team2.robots

                for other in all_robots:
                    if other == robot:
                        continue
                    ox = other.pose['x']
                    oy = other.pose['y']

                    future_x = robot.pose['x'] + vx
                    future_y = robot.pose['y'] + vy
                    dist_to_other = math.hypot(future_x - ox, future_y - oy)

                    min_safe_distance = (ROBOT_SIZE / self.SCALE) + 0.1  # chuyển về đơn vị mét

                    if dist_to_other < min_safe_distance:
                        safe = False
                        break

                if safe:
                    # Nếu an toàn mới di chuyển
                    robot.pose['x'] += vx
                    robot.pose['y'] += vy

                    px = self.field.MARGIN + (robot.pose['x'] + 11.0) * self.SCALE - ROBOT_SIZE / 2
                    py = self.field.MARGIN + (robot.pose['y'] + 7.0) * self.SCALE - ROBOT_SIZE / 2
                    robot.setPos(px, py)

    def is_inside_field(self, x, y):
        return -12.0 <= x <= 12.0 and -8.0 <= y <= 8.0

    def check_game_state(self):
        for red_robot in self.team2.robots:
            if self.field.target_zone.contains(red_robot.pose['x'], red_robot.pose['y']):
                print("Red team wins!")
                self.labelGameState.setText("Team Red Wins!")
                self.is_running = False
                self.pushButton_Start.setText("Start")
                return
        blocked = 0
        block_distance = 0.5

        for red_robot in self.team2.robots:
            for blue_robot in self.team1.robots:
                dx = red_robot.pose['x'] - blue_robot.pose['x']
                dy = red_robot.pose['y'] - blue_robot.pose['y']
                dist = math.hypot(dx, dy)
                if dist <= block_distance:
                    blocked += 1
                    break
        if blocked == len(self.team2.robots):
            print("Blue team wins!")
            self.labelGameState.setText("Team Blue Wins!")
            self.is_running = False
            self.pushButton_Start.setText("Start")
        else:
            self.labelGameState.setText("Game Running...")
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
