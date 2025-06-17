from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsRectItem, QGraphicsPathItem
from PyQt5.QtGui import QBrush, QPen, QPainterPath
from PyQt5.QtCore import Qt
from config import SCALE, ROBOT_SIZE

class Team:
    def __init__(self, team_id: int, color: Qt.GlobalColor, margin: float, scene, y_start=2.0):
        self.team_id = team_id
        self.color = color
        self.margin = margin
        self.scene = scene
        self.y_start = y_start

        self.robots = []
        self.robot_size = ROBOT_SIZE * SCALE  # pixel

    def create_robot_graphic(self, x_meter, y_meter, robot_id, theta=0.0):
        # Chuyển từ tọa độ vật lý (gốc giữa sân) sang Qt
        x_pix = self.margin + (x_meter + 11.0) * SCALE - self.robot_size / 2
        y_pix = self.margin + (y_meter + 7.0) * SCALE - self.robot_size / 2

        # Thân robot
        body = QGraphicsRectItem(0, 0, self.robot_size, self.robot_size)
        body.setBrush(QBrush(self.color))
        body.setPen(QPen(Qt.black, 2))

        # Hình tam giác lớn chỉ hướng
        triangle = QGraphicsPathItem()
        path = QPainterPath()
        path.moveTo(self.robot_size * 0.9, self.robot_size / 2)
        path.lineTo(self.robot_size * 0.4, self.robot_size * 0.2)
        path.lineTo(self.robot_size * 0.4, self.robot_size * 0.8)
        path.closeSubpath()
        triangle.setPath(path)
        triangle.setBrush(QBrush(Qt.white))
        triangle.setPen(QPen(Qt.NoPen))

        group = QGraphicsItemGroup()
        group.addToGroup(body)
        group.addToGroup(triangle)
        group.setPos(x_pix, y_pix)
        group.setTransformOriginPoint(self.robot_size / 2, self.robot_size / 2)
        group.setRotation(theta % 360)

        group.pose = {'x': x_meter, 'y': y_meter, 'theta': theta % 360}
        group.team = self.team_id
        group.robot_id = robot_id
        group.has_ball = False

        return group

    def create_robots(self, number: int, positions=None, on_created=None):
        self.clear_robots()
        self.robots = []

        if positions is None:
            # Mặc định sinh tự động như hiện tại
            for i in range(number):
                x = -7.0 if self.team_id == 1 else 7.0
                y = self.y_start + i * 1.5
                theta = 0 if self.team_id == 1 else 180

                robot = self.create_robot_graphic(x, y, i, theta)
                self.robots.append(robot)
                self.scene.addItem(robot)
                if on_created:
                    on_created(robot)
        else:
            # Sinh theo vị trí chỉ định
            for i, (x, y, theta) in enumerate(positions):
                robot = self.create_robot_graphic(x, y, i, theta)
                self.robots.append(robot)
                self.scene.addItem(robot)
                if on_created:
                    on_created(robot)

    def clear_robots(self):
        for robot in self.robots:
            self.scene.removeItem(robot)
        self.robots = []
