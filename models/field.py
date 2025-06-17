from PyQt5.QtWidgets import (QGraphicsRectItem, QGraphicsLineItem,
                             QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsScene)
from PyQt5.QtGui import QBrush, QPen, QColor, QPainterPath
from PyQt5.QtCore import Qt, QRectF, QPointF
from zones.target_zone import CircleZone, RectangleZone, DiamondZone, SemiCircleZone
from zones.target_zone_drawer import draw_target_zone
import math

class Field:
    def __init__(self, scale: float):
        self.SCALE = scale
        self.init_parameters()
        #self.target_zone = CircleZone(0.0, 0.0, 1.5)
        
        #self.target_zone = RectangleZone(0.0, 0.0, 5.0, 3.0)
        
        #self.target_zone = DiamondZone(11.0, 0.0, 2.0, 2.0)
        
        self.target_zone = SemiCircleZone(11.0, 0.0, 2.0, direction='left')

    def init_parameters(self):
        self.FIELD_WIDTH = 22 * self.SCALE
        self.FIELD_HEIGHT = 14 * self.SCALE
        self.MARGIN = 1 * self.SCALE
        self.WIDTH = self.FIELD_WIDTH + 2 * self.MARGIN
        self.HEIGHT = self.FIELD_HEIGHT + 2 * self.MARGIN

        self.C = 6.9 * self.SCALE
        self.D = 3.9 * self.SCALE
        self.E = 2.25 * self.SCALE
        self.F = 0.75 * self.SCALE
        self.G = 0.75 * self.SCALE
        self.H = 2 * self.SCALE / 2
        self.I = 3.6 * self.SCALE
        self.J = 0.15 * self.SCALE / 2
        self.K = int(0.125 * self.SCALE)
        self.GOAL_DEPTH = 0.7 * self.SCALE
        self.GOAL_HEIGHT = 2.5 * self.SCALE

    def draw(self, scene: QGraphicsScene):
        scene.clear()
        self.draw_background(scene)
        self.draw_border(scene)
        self.draw_center_line(scene)
        self.draw_center_circle(scene)
        self.draw_penalty_area(scene, self.MARGIN, True)
        self.draw_penalty_area(scene, self.WIDTH - self.MARGIN, False)
        self.draw_corners(scene)
        self.draw_goal(scene, self.MARGIN - self.GOAL_DEPTH, True)
        self.draw_goal(scene, self.WIDTH - self.MARGIN, False)

        self.draw_target_zone(scene)

    def draw_background(self, scene):
        field = QGraphicsRectItem(0, 0, self.WIDTH, self.HEIGHT)
        field.setBrush(QBrush(QColor(0, 153, 0)))
        scene.addItem(field)

    def draw_border(self, scene):
        border = QGraphicsRectItem(self.MARGIN, self.MARGIN,
                                   self.FIELD_WIDTH, self.FIELD_HEIGHT)
        border.setPen(QPen(Qt.white, self.K))
        border.setBrush(QBrush(Qt.NoBrush))
        scene.addItem(border)

    def draw_center_line(self, scene):
        center_line = QGraphicsLineItem(self.WIDTH / 2, self.MARGIN,
                                        self.WIDTH / 2, self.HEIGHT - self.MARGIN)
        center_line.setPen(QPen(Qt.white, self.K))
        scene.addItem(center_line)

    def draw_center_circle(self, scene):
        center = QPointF(self.WIDTH / 2, self.HEIGHT / 2)
        circle = QGraphicsEllipseItem(center.x() - self.H, center.y() - self.H,
                                      2 * self.H, 2 * self.H)
        circle.setPen(QPen(Qt.white, self.K))
        scene.addItem(circle)

        dot = QGraphicsEllipseItem(center.x() - self.J, center.y() - self.J,
                                   2 * self.J, 2 * self.J)
        dot.setBrush(QBrush(Qt.white))
        dot.setPen(QPen(Qt.NoPen))
        scene.addItem(dot)

    def draw_penalty_area(self, scene, x_pos, is_left):
        rect = QGraphicsRectItem(x_pos, self.HEIGHT / 2 - self.C / 2,
                                 self.E if is_left else -self.E, self.C)
        rect.setPen(QPen(Qt.white, self.K))
        rect.setBrush(QBrush(Qt.NoBrush))
        scene.addItem(rect)

        dot_x = x_pos + (self.I if is_left else -self.I)
        penalty_dot = QGraphicsEllipseItem(dot_x - self.J, self.HEIGHT / 2 - self.J,
                                           2 * self.J, 2 * self.J)
        penalty_dot.setBrush(QBrush(Qt.white))
        penalty_dot.setPen(QPen(Qt.NoPen))
        scene.addItem(penalty_dot)

        small_rect = QGraphicsRectItem(x_pos, self.HEIGHT / 2 - self.D / 2,
                                       self.F if is_left else -self.F, self.D)
        small_rect.setPen(QPen(Qt.white, self.K))
        small_rect.setBrush(QBrush(Qt.NoBrush))
        scene.addItem(small_rect)

    def draw_corners(self, scene):
        positions = [
            (self.MARGIN, self.MARGIN, 3 * math.pi / 2, 2 * math.pi),
            (self.MARGIN, self.HEIGHT - self.MARGIN, 0, math.pi / 2),
            (self.WIDTH - self.MARGIN, self.MARGIN, math.pi, 3 * math.pi / 2),
            (self.WIDTH - self.MARGIN, self.HEIGHT - self.MARGIN, math.pi / 2, math.pi)
        ]
        for x, y, start_angle, end_angle in positions:
            path = QPainterPath()
            path.moveTo(x, y)
            path.arcTo(x - self.G, y - self.G, 2 * self.G, 2 * self.G,
                       start_angle * 180 / math.pi, (end_angle - start_angle) * 180 / math.pi)
            corner = QGraphicsPathItem(path)
            corner.setPen(QPen(Qt.white, self.K))
            scene.addItem(corner)

    def draw_goal(self, scene, x_pos, is_left):
        goal = QGraphicsRectItem(x_pos, self.HEIGHT / 2 - self.GOAL_HEIGHT / 2,
                                 self.GOAL_DEPTH, self.GOAL_HEIGHT)
        goal.setPen(QPen(Qt.white, self.K))
        goal.setBrush(QBrush(Qt.NoBrush))
        scene.addItem(goal)

        net_x = x_pos if is_left else x_pos + self.GOAL_DEPTH
        net_w = -self.GOAL_DEPTH * 0.3 if is_left else self.GOAL_DEPTH * 0.3
        net = QGraphicsRectItem(net_x, self.HEIGHT / 2 - self.GOAL_HEIGHT / 2,
                                net_w, self.GOAL_HEIGHT)
        net.setBrush(QBrush(QColor(255, 255, 255, 100)))
        net.setPen(QPen(Qt.NoPen))
        scene.addItem(net)

    def get_dimensions(self):
        return self.WIDTH, self.HEIGHT
    
    def draw_target_zone(self, scene):
        draw_target_zone(scene, self.target_zone, self.SCALE, self.MARGIN)
