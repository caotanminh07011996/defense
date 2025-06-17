# zones/target_zone.py

import math

class TargetZone:
    """
    Lớp cơ sở cho các loại vùng target zone.
    Các lớp con cần cài đặt hàm contains().
    """
    def contains(self, x, y):
        raise NotImplementedError("Subclasses must implement this method.")


class CircleZone(TargetZone):
    def __init__(self, center_x, center_y, radius):
        self.cx = center_x
        self.cy = center_y
        self.radius = radius

    def contains(self, x, y):
        dist = math.hypot(self.cx - x, self.cy - y)
        return dist <= self.radius


class RectangleZone(TargetZone):
    def __init__(self, center_x, center_y, width, height):
        self.cx = center_x
        self.cy = center_y
        self.w = width
        self.h = height

    def contains(self, x, y):
        return (self.cx - self.w/2 <= x <= self.cx + self.w/2 and
                self.cy - self.h/2 <= y <= self.cy + self.h/2)


class DiamondZone(TargetZone):
    def __init__(self, center_x, center_y, width, height):
        self.cx = center_x
        self.cy = center_y
        self.w = width
        self.h = height

    def contains(self, x, y):
        dx = abs(x - self.cx) / (self.w / 2)
        dy = abs(y - self.cy) / (self.h / 2)
        return dx + dy <= 1


class SemiCircleZone(TargetZone):
    """
    direction:
        - 'right': nửa hình tròn mở về bên phải
        - 'left': mở về bên trái
        - 'up': mở lên trên
        - 'down': mở xuống dưới
    """
    def __init__(self, center_x, center_y, radius, direction='right'):
        self.cx = center_x
        self.cy = center_y
        self.radius = radius
        self.direction = direction

    def contains(self, x, y):
        dist = math.hypot(self.cx - x, self.cy - y)
        if dist > self.radius:
            return False

        if self.direction == 'right':
            return x >= self.cx
        elif self.direction == 'left':
            return x <= self.cx
        elif self.direction == 'up':
            return y >= self.cy
        elif self.direction == 'down':
            return y <= self.cy
        else:
            return False
