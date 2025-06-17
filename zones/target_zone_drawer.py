# zones/target_zone_drawer.py

from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsPathItem
from PyQt5.QtGui import QPen, QColor, QBrush, QPainterPath
from PyQt5.QtCore import Qt

from zones.target_zone import CircleZone, RectangleZone, DiamondZone, SemiCircleZone

def draw_target_zone(scene, target_zone, scale, margin):
    pen = QPen(QColor(255, 0, 0), 2, Qt.DashLine)
    brush = QBrush(QColor(255, 255, 0, 100))

    if isinstance(target_zone, CircleZone):
        cx_pix = margin + (target_zone.cx + 11.0) * scale
        cy_pix = margin + (target_zone.cy + 7.0) * scale
        radius_pix = target_zone.radius * scale

        ellipse = QGraphicsEllipseItem(cx_pix - radius_pix, cy_pix - radius_pix,
                                        2 * radius_pix, 2 * radius_pix)
        ellipse.setPen(pen)
        ellipse.setBrush(brush)
        scene.addItem(ellipse)

    elif isinstance(target_zone, RectangleZone):
        cx_pix = margin + (target_zone.cx + 11.0) * scale
        cy_pix = margin + (target_zone.cy + 7.0) * scale
        w_pix = target_zone.w * scale
        h_pix = target_zone.h * scale

        rect = QGraphicsRectItem(cx_pix - w_pix/2, cy_pix - h_pix/2, w_pix, h_pix)
        rect.setPen(pen)
        rect.setBrush(brush)
        scene.addItem(rect)

    elif isinstance(target_zone, DiamondZone):
        cx_pix = margin + (target_zone.cx + 11.0) * scale
        cy_pix = margin + (target_zone.cy + 7.0) * scale
        w_pix = target_zone.w * scale
        h_pix = target_zone.h * scale

        path = QPainterPath()
        path.moveTo(cx_pix, cy_pix - h_pix/2)
        path.lineTo(cx_pix + w_pix/2, cy_pix)
        path.lineTo(cx_pix, cy_pix + h_pix/2)
        path.lineTo(cx_pix - w_pix/2, cy_pix)
        path.closeSubpath()

        diamond = QGraphicsPathItem(path)
        diamond.setPen(pen)
        diamond.setBrush(brush)
        scene.addItem(diamond)

    elif isinstance(target_zone, SemiCircleZone):
        cx_pix = margin + (target_zone.cx + 11.0) * scale
        cy_pix = margin + (target_zone.cy + 7.0) * scale
        radius_pix = target_zone.radius * scale

        path = QPainterPath()

        if target_zone.direction == 'right':
            start_angle = 270  # Bắt đầu từ phía trên (12h)
            span_angle = 180   # vẽ ngược chiều kim đồng hồ sang phải
        elif target_zone.direction == 'left':
            start_angle = 90   # Bắt đầu từ phía dưới (6h)
            span_angle = 180   # vẽ ngược chiều kim đồng hồ sang trái
        elif target_zone.direction == 'up':
            start_angle = 0
            span_angle = 180
        elif target_zone.direction == 'down':
            start_angle = 180
            span_angle = 180

        path.moveTo(cx_pix, cy_pix)
        path.arcTo(cx_pix - radius_pix, cy_pix - radius_pix, 2 * radius_pix, 2 * radius_pix,
                   start_angle, span_angle)
        path.closeSubpath()

        semi = QGraphicsPathItem(path)
        semi.setPen(pen)
        semi.setBrush(brush)
        scene.addItem(semi)

    else:
        print("Unknown target zone type!")
