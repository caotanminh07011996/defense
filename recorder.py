import csv
import time
import os
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtGui import QBrush, QPen



class Recorder:
    def __init__(self, team1, team2, interval_ms=50):
        """
        Ghi lại trạng thái các robot và bóng theo chu kỳ.

        Args:
            team1: đối tượng Team 1 (có thuộc tính `robots`)
            team2: đối tượng Team 2 (có thuộc tính `robots`)
            ball:  đối tượng Ball (có thuộc tính `x`, `y`)
            interval_ms (int): thời gian giữa mỗi lần ghi (ms)
        """
        self.team1 = team1
        self.team2 = team2
        
        self.interval_ms = interval_ms

        self.timer = QTimer()
        self.timer.timeout.connect(self.save_pose_data)
        self.saving = False

    def start(self, filename=None):
        """Bắt đầu ghi dữ liệu"""
        os.makedirs("data", exist_ok=True)

        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"data/snapshot_{timestamp}.csv"

        self.save_file = open(filename, "w", newline="")
        self.save_writer = csv.writer(self.save_file)
        self.start_time = time.time()

        # Ghi header
        header = ["Time"]
        all_robots = self.team1.robots + self.team2.robots
        for i, robot in enumerate(all_robots):
            header += [f"R{i}_team", f"R{i}_id", f"R{i}_x", f"R{i}_y", f"R{i}_theta"]
        #header += ["Ball_x", "Ball_y"]
        self.save_writer.writerow(header)

        self.timer.start(self.interval_ms)
        self.saving = True
        print(f"[Recorder] Started saving to {filename}")

    def stop(self):
        """Dừng ghi và đóng file"""
        if self.saving:
            self.timer.stop()
            self.save_file.close()
            self.saving = False
            print(f"[Recorder] Stopped saving.")

    def save_pose_data(self):
        """Ghi 1 dòng trạng thái hiện tại"""
        now = time.time() - self.start_time
        row = [f"{now:.2f}"]

        all_robots = self.team1.robots + self.team2.robots
        for robot in all_robots:
            pose = robot.pose
            row += [robot.team, robot.robot_id,
                    f"{pose['x']:.2f}", f"{pose['y']:.2f}", f"{pose['theta']:.2f}"]

        #row += [f"{self.ball.x:.2f}", f"{self.ball.y:.2f}"]
        self.save_writer.writerow(row)



class Replayer:
    def __init__(self, scene, team1, team2, scale, margin, robot_size):
        """
        Phát lại trạng thái robot và bóng từ file CSV.

        Args:
            scene: QGraphicsScene
            team1: Team 1 object
            team2: Team 2 object
            ball: Ball object
            scale (float): tỉ lệ pixel / mét
            margin (float): khoảng lề sân
            robot_size (float): kích thước hiển thị robot (pixel)
        """
        self.scene = scene
        self.team1 = team1
        self.team2 = team2
        #self.ball = ball
        self.SCALE = scale
        self.MARGIN = margin
        self.ROBOT_SIZE = robot_size

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.current_index = 0

    def load_csv(self, file_path):
        """Tải dữ liệu replay từ file CSV"""
        with open(file_path, "r") as f:
            reader = csv.reader(f)
            self.headers = next(reader)
            self.frames = list(reader)
        self.current_index = 0
        print(f"[Replayer] Loaded {len(self.frames)} frames from {file_path}")

        # Tự khởi tạo robots theo frame đầu
        self.team1.clear_robots()
        self.team2.clear_robots()
        first_row = self.frames[0]
        num_robots = (len(first_row) - 1 - 2) // 5
        for i in range(num_robots):
            idx = 1 + i * 5
            team = int(first_row[idx])
            robot_id = int(first_row[idx + 1])
            x = float(first_row[idx + 2])
            y = float(first_row[idx + 3])
            theta = float(first_row[idx + 4])
            color = Qt.blue if team == 1 else Qt.red

            robot = self.team1.create_robot_graphic(x, y, robot_id, theta) if team == 1 \
                    else self.team2.create_robot_graphic(x, y, robot_id, theta)

            self.scene.addItem(robot)
            (self.team1.robots if team == 1 else self.team2.robots).append(robot)

        #self.ball_graphic = None
        #self.update_ball_graphic(first_row)

    '''
    def update_ball_graphic(self, row):
        """Vẽ bóng tại vị trí row"""
        ball_x = float(row[-2])
        ball_y = float(row[-1])
        self.ball.x = ball_x
        self.ball.y = ball_y

        if self.ball_graphic:
            self.scene.removeItem(self.ball_graphic)

        radius = 0.12 * self.SCALE
        cx = self.MARGIN + ball_x * self.SCALE
        cy = self.MARGIN + ball_y * self.SCALE

        ellipse = QGraphicsEllipseItem(cx - radius, cy - radius, 2 * radius, 2 * radius)
        ellipse.setBrush(QBrush(Qt.white))
        ellipse.setPen(QPen(Qt.black, 1))
        self.scene.addItem(ellipse)
        self.ball_graphic = ellipse
    '''

    def start(self):
        if self.frames:
            self.timer.start(50)

    def stop(self):
        self.timer.stop()

    def update_frame(self):
        if self.current_index >= len(self.frames):
            self.current_index = 0  # Lặp lại từ đầu

        row = self.frames[self.current_index]
        self.current_index += 1

        all_robots = self.team1.robots + self.team2.robots
        for i, robot in enumerate(all_robots):
            idx = 1 + i * 5
            x = float(row[idx + 2])
            y = float(row[idx + 3])
            theta = float(row[idx + 4])

            px = self.MARGIN + x * self.SCALE - self.ROBOT_SIZE / 2
            py = self.MARGIN + y * self.SCALE - self.ROBOT_SIZE / 2
            robot.setPos(px, py)
            robot.setRotation(theta)

            robot.pose['x'] = x
            robot.pose['y'] = y
            robot.pose['theta'] = theta

        #self.update_ball_graphic(row)