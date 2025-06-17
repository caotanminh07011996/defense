import math
import heapq


class HybridAStarPlanner:
    def __init__(self, obstacles, robot_radius, xy_resolution=0.1, theta_resolution=15.0,
                 max_steer=30.0, step_size=0.5):
        """
        obstacles: list of (x,y)
        """
        self.obstacles = obstacles
        self.robot_radius = robot_radius
        self.xy_resolution = xy_resolution
        self.theta_resolution = math.radians(theta_resolution)
        self.max_steer = math.radians(max_steer)
        self.step_size = step_size

        self.steer_set = [-self.max_steer, 0.0, self.max_steer]

    def plan(self, start, goal):
        sx, sy, stheta = start
        gx, gy = goal

        open_set = []
        closed_set = set()

        h_start = self.calc_heuristic(sx, sy, gx, gy)
        heapq.heappush(open_set, (h_start, 0.0, (sx, sy, stheta), None))
        came_from = dict()

        while open_set:
            f, cost, current, parent = heapq.heappop(open_set)
            x, y, theta = current

            node_id = self.state_index(x, y, theta)
            if node_id in closed_set:
                continue

            came_from[node_id] = (current, parent)
            closed_set.add(node_id)

            if math.hypot(x - gx, y - gy) < self.xy_resolution:
                return self.reconstruct_path(came_from, current)

            for steer in self.steer_set:
                new_x, new_y, new_theta = self.forward(x, y, theta, steer)
                if not self.check_collision(new_x, new_y):
                    new_cost = cost + self.step_size
                    h = self.calc_heuristic(new_x, new_y, gx, gy)
                    heapq.heappush(open_set, (new_cost + h, new_cost, (new_x, new_y, new_theta), current))

        return None  # không tìm được đường

    def forward(self, x, y, theta, steer):
        theta_new = theta + steer
        theta_new = self.normalize_angle(theta_new)
        x_new = x + self.step_size * math.cos(theta_new)
        y_new = y + self.step_size * math.sin(theta_new)
        return x_new, y_new, theta_new

    def check_collision(self, x, y):
        for ox, oy in self.obstacles:
            dist = math.hypot(x - ox, y - oy)
            if dist <= self.robot_radius + 0.1:
                return True
        return False

    def calc_heuristic(self, x, y, gx, gy):
        return math.hypot(x - gx, y - gy)

    def state_index(self, x, y, theta):
        xi = round(x / self.xy_resolution)
        yi = round(y / self.xy_resolution)
        ti = round(theta / self.theta_resolution)
        return (xi, yi, ti)

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def reconstruct_path(self, came_from, current):
        path = []
        node_id = self.state_index(*current)
        while node_id in came_from:
            state, parent = came_from[node_id]
            path.append(state)
            if parent is None:
                break
            node_id = self.state_index(*parent)
        return path[::-1]
