# fog_nodes.py
# Simulation des nœuds Fog - correspond aux variables node_load,
# node_capacity, task_assignment de R1/R2/R3

class FogNode:
    def __init__(self, node_id, capacity):
        self.node_id = node_id          # identifiant du nœud
        self.capacity = capacity         # node_capacity de R1
        self.load = 0                    # node_load de R1
        self.task_assignment = {}        # task_assignment de R1
        self.is_active = True            # état du nœud

    def can_accept(self):
        # garde : node_load(n) < node_capacity(n)
        return self.is_active and self.load < self.capacity

    def assign_task(self, task_id):
        # act : task_assignment(t) := n, node_load(n) := node_load(n) + 1
        if self.can_accept():
            self.task_assignment[task_id] = self.node_id
            self.load += 1
            return True
        return False

    def complete_task(self, task_id):
        # act : node_load(n) := node_load(n) - 1
        if task_id in self.task_assignment:
            del self.task_assignment[task_id]
            self.load -= 1
            return True
        return False

    def simulate_failure(self):
        # NODE_FAILURE : node_load(n) := 0
        failed_tasks = list(self.task_assignment.keys())
        self.task_assignment = {}
        self.load = 0
        self.is_active = False
        return failed_tasks

    def __str__(self):
        return (f"Node {self.node_id} | "
                f"Load: {self.load}/{self.capacity} | "
                f"Active: {self.is_active}")


class FogNetwork:
    def __init__(self, num_nodes=3, capacity=5):
        # initialisation : node_capacity := NODES x {max_load}
        self.nodes = {
            f"N{i}": FogNode(f"N{i}", capacity)
            for i in range(1, num_nodes + 1)
        }

    def get_active_nodes(self):
        return [n for n in self.nodes.values() if n.is_active]

    def get_node(self, node_id):
        return self.nodes.get(node_id)

    def print_status(self):
        print("\n=== État des nœuds Fog ===")
        for node in self.nodes.values():
            print(node)