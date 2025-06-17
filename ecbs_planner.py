import math
import heapq
import copy

class Constraint:
    def __init__(self, agent, pos, timestep):
        self.agent = agent
        self.pos = pos
        self.timestep = timestep

class ECBSNode:
    def __init__(self, paths, constraints, cost, conflicts):
        self.paths = paths
        self.constraints = constraints
        self.cost = cost
        self.conflicts = conflicts

    def __lt__(self, other):
        return self.cost < other.cost  # sort by path cost in open list

class ECBSPlanner:
    def __init__(self, agent_ids, planner, safe_distance=0.5, epsilon=1.5, pose_lookup=None):
        self.agent_ids = agent_ids
        self.planner = planner
        self.safe_distance = safe_distance
        self.epsilon = epsilon
        self.pose_lookup = pose_lookup

    def find_solution(self, goal):
        initial_paths = {}
        for agent in self.agent_ids:
            start_pose = self.pose_lookup(agent)
            path = self.planner.plan(start_pose, goal)
            if path is None:
                return None
            initial_paths[agent] = path

        root = ECBSNode(
            paths=initial_paths,
            constraints=[],
            cost=self.total_cost(initial_paths),
            conflicts=self.count_conflicts(initial_paths)
        )

        open_list = []
        focal_list = []

        heapq.heappush(open_list, (root.cost, root))
        heapq.heappush(focal_list, (root.conflicts, root))

        best_cost = root.cost

        while focal_list:
            _, node = heapq.heappop(focal_list)

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
                cost = self.total_cost(new_paths)
                conflicts = self.count_conflicts(new_paths)
                new_node = ECBSNode(new_paths, new_constraints, cost, conflicts)

                heapq.heappush(open_list, (cost, new_node))

            # Update focal list after expansion
            focal_list = [
                (n.conflicts, n) for cost, n in open_list if cost <= self.epsilon * best_cost
            ]
            heapq.heapify(focal_list)

            if open_list:
                best_cost = open_list[0][0]

        return None

    def total_cost(self, paths):
        return sum(len(p) for p in paths.values())

    def count_conflicts(self, paths):
        count = 0
        max_t = max(len(p) for p in paths.values())
        for t in range(max_t):
            positions = []
            for agent, path in paths.items():
                if t < len(path):
                    x, y, _ = path[t]
                else:
                    x, y, _ = path[-1]
                positions.append((agent, x, y))

            for i in range(len(positions)):
                for j in range(i+1, len(positions)):
                    ai, xi, yi = positions[i]
                    aj, xj, yj = positions[j]
                    dist = math.hypot(xi - xj, yi - yj)
                    if dist < self.safe_distance:
                        count += 1
        return count

    def detect_conflict(self, paths):
        max_t = max(len(p) for p in paths.values())
        for t in range(max_t):
            positions = []
            for agent, path in paths.items():
                if t < len(path):
                    x, y, _ = path[t]
                else:
                    x, y, _ = path[-1]
                positions.append((agent, x, y))

            for i in range(len(positions)):
                for j in range(i+1, len(positions)):
                    ai, xi, yi = positions[i]
                    aj, xj, yj = positions[j]
                    dist = math.hypot(xi - xj, yi - yj)
                    if dist < self.safe_distance:
                        pos_conflict = ((xi + xj) / 2, (yi + yj) / 2)
                        return ai, aj, t, pos_conflict
        return None

    def replan(self, agent, constraints, goal):
        def is_constrained(pos, timestep):
            for c in constraints:
                if c.agent == agent and c.timestep == timestep:
                    if math.hypot(pos[0] - c.pos[0], pos[1] - c.pos[1]) < self.safe_distance:
                        return True
            return False

        start_pose = self.pose_lookup(agent)
        raw_path = self.planner.plan(start_pose, goal)
        if raw_path is None:
            return None

        new_path = []
        for t, (x, y, theta) in enumerate(raw_path):
            if is_constrained((x, y), t):
                return None
            new_path.append((x, y, theta))

        return new_path
