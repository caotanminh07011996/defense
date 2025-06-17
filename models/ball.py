# models/ball.py

from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtGui import QBrush, QPen, QColor
import math
from PyQt5.QtCore import Qt

class Ball:
    def __init__(self, x, y, scene, scale, margin):
        self.x = x
        self.y = y
        self.vx = 0.0  # vận tốc x (m/s)
        self.vy = 0.0  # vận tốc y (m/s)
        self.mass = 0.5  # khối lượng (kg)
        self.radius = 0.12  # bán kính bóng (m)
        self.friction = 0.4  # hệ số ma sát

        self.scene = scene
        self.scale = scale
        self.margin = margin
        self.graphic = None
        self.draw()  # vẽ ban đầu

    def get_position(self):
        return self.x, self.y

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.draw()
    '''
    def kick(self, force, angle_rad):
        """
        Tác động lực sút → tạo vận tốc tức thời.
        """
        acceleration = force / self.mass
        self.vx = acceleration * math.cos(angle_rad)
        self.vy = acceleration * math.sin(angle_rad)
    '''

    def kick(self, force: float, angle_rad: float, team: int):
        """
        Gán vận tốc cho bóng theo hướng và lực.

        Args:
            force (float): lực sút (N)
            angle_rad (float): góc quay của robot (radian)
            team (int): team của robot (1 hoặc 2)
        """
        mass = 0.5  # kg
        speed = force / mass  # m/s

        #direction = 1 if team == 1 else -1
        direction = 1 


        self.vx = direction * speed * math.cos(angle_rad)
        self.vy = direction * speed * math.sin(angle_rad)  # y ngược trục Qt


    def update(self, dt):
        """
        Cập nhật vị trí bóng theo thời gian.
        Args:
            dt (float): delta time (s)
        """
        speed = math.hypot(self.vx, self.vy)
        if speed < 0.01:
            self.vx = self.vy = 0
            return

        # Lực ma sát gây giảm tốc
        friction_acc = self.friction * 9.81
        decel = friction_acc * dt

        new_speed = max(0, speed - decel)
        if new_speed == 0:
            self.vx = self.vy = 0
        else:
            self.vx *= new_speed / speed
            self.vy *= new_speed / speed

        # Cập nhật vị trí
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self):
        if self.graphic:
            self.scene.removeItem(self.graphic)

        radius_pix = self.radius * self.scale
        cx = self.margin + (self.x + 11.0) * self.scale
        cy = self.margin + (self.y + 7.0) * self.scale

        self.graphic = QGraphicsEllipseItem(
            cx - radius_pix, cy - radius_pix,
            2 * radius_pix, 2 * radius_pix
        )
        self.graphic.setBrush(QBrush(QColor("orange")))
        self.graphic.setPen(QPen(Qt.black, 1))
        self.scene.addItem(self.graphic)

