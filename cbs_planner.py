import math
import heapq
import copy

class Constraint:
    def __init__(self, agent, pos, timestep):
        self.agent = agent
        self.pos = pos
        self.timestep = timestep

class CBSNode:
    def __init__(self, paths, constraints, cost):
        self.paths = paths
        self.constraints = constraints
        self.cost = cost

    def __lt__(self, other):
        return self.cost < other.cost

class CBSPlanner:
    def __init__(self, agent_ids, planner, safe_distance=0.6, pose_lookup=None):
        self.agent_ids = agent_ids  # list of robot IDs
        self.planner = planner
        self.safe_distance = safe_distance
        self.pose_lookup = pose_lookup  # callable (robot_id) -> (x,y,theta)

    def find_solution(self, goal):
        # Initial independent plan
        initial_paths = {}
        for agent_id in self.agent_ids:
            start_pose = self.pose_lookup(agent_id)
            path = self.planner.plan(start_pose, goal)
            if path is None:
                return None
            initial_paths[agent_id] = path

        root = CBSNode(paths=initial_paths, constraints=[], cost=self.total_cost(initial_paths))
        open_list = [root]

        while open_list:
            node = heapq.heappop(open_list)
            conflict = self.detect_conflict(node.paths)
            if not conflict:
                return node.paths

            agent1, agent2, t, pos = conflict

            for agent in [agent1, agent2]:
                new_constraints = node.constraints + [Constraint(agent, pos, t)]
                new_paths = copy.deepcopy(node.paths)

                replanned_path = self.replan(agent, new_constraints, goal)
                if replanned_path is None:
                    continue

                new_paths[agent] = replanned_path
                new_node = CBSNode(new_paths, new_constraints, self.total_cost(new_paths))
                heapq.heappush(open_list, new_node)

        return None

    def total_cost(self, paths):
        return sum(len(p) for p in paths.values())

    def detect_conflict(self, paths):
        max_t = max(len(p) for p in paths.values())
        for t in range(max_t):
            positions = []
            for agent_id, path in paths.items():
                if t < len(path):
                    x, y, _ = path[t]
                else:
                    x, y, _ = path[-1]
                positions.append((agent_id, x, y))

            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    ai, xi, yi = positions[i]
                    aj, xj, yj = positions[j]
                    dist = math.hypot(xi - xj, yi - yj)
                    if dist < self.safe_distance:
                        pos_conflict = ((xi + xj) / 2, (yi + yj) / 2)
                        return ai, aj, t, pos_conflict
        return None

    def replan(self, agent_id, constraints, goal):
        def is_constrained(pos, timestep):
            for c in constraints:
                if c.agent == agent_id and c.timestep == timestep:
                    if math.hypot(pos[0] - c.pos[0], pos[1] - c.pos[1]) < self.safe_distance:
                        return True
            return False

        start_pose = self.pose_lookup(agent_id)
        raw_path = self.planner.plan(start_pose, goal)

        if raw_path is None:
            return None

        new_path = []
        for t, (x, y, theta) in enumerate(raw_path):
            if is_constrained((x, y), t):
                return None
            new_path.append((x, y, theta))

        return new_path
