import math

class Robot:
    def __init__(self, x: float, y: float, theta: float = 0.0):
        """
        Robot mô phỏng với trạng thái vị trí và vận tốc.

        Args:
            x (float): Tọa độ x (mét)
            y (float): Tọa độ y (mét)
            theta (float): Góc quay (độ)
        """
        self.x = x
        self.y = y
        self.theta = theta  # độ

        self.vx = 0.0       # vận tốc theo trục x (m/s)
        self.vy = 0.0       # vận tốc theo trục y (m/s)
        self.vtheta = 0.0   # vận tốc góc (độ/s)

    def update(self, dt: float):
        """
        Cập nhật vị trí và góc quay của robot sau thời gian dt (giây)

        Args:
            dt (float): bước thời gian (timestep)
        """
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.theta += self.vtheta * dt
        self.theta %= 360  # giữ góc trong khoảng [0, 360)

    def set_pose(self, x: float, y: float, theta: float):
        """Gán lại trạng thái vị trí và góc quay"""
        self.x = x
        self.y = y
        self.theta = theta % 360

    def set_velocity(self, vx: float, vy: float, vtheta: float):
        """Gán vận tốc tuyến tính và góc quay"""
        self.vx = vx
        self.vy = vy
        self.vtheta = vtheta

    def get_pose(self):
        """Trả về tuple (x, y, theta)"""
        return self.x, self.y, self.theta

    def get_velocity(self):
        """Trả về tuple (vx, vy, vtheta)"""
        return self.vx, self.vy, self.vtheta

    def __repr__(self):
        return (f"Robot(x={self.x:.2f}, y={self.y:.2f}, θ={self.theta:.1f}°, "
                f"vx={self.vx:.2f}, vy={self.vy:.2f}, vθ={self.vtheta:.2f})")
