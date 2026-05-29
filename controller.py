# controller.py
# Simulation du contrôleur Fog - correspond à CONTROLLER_ASSIGN de R3
# Le contrôleur choisit le nœud optimal pour chaque tâche

class FogController:
    def __init__(self, fog_network):
        self.network = fog_network
        # controller_decision de R3
        self.controller_decision = {}
        # audit_log de R3
        self.audit_log = []

    def assign_node(self, task_id, priority):
        """
        CONTROLLER_ASSIGN de R3 :
        - Choisit le nœud avec la charge minimale
        - Les tâches critical ont la priorité absolue
        """
        active_nodes = self.network.get_active_nodes()

        if not active_nodes:
            print(f"[ERREUR] Aucun nœud disponible pour la tâche {task_id}")
            return None

        # grd5 : n est le nœud avec node_load minimal
        if priority == "critical":
            # Tâche ECG critique : nœud le moins chargé
            best_node = min(active_nodes, key=lambda n: n.load)
        else:
            # Tâche normale : premier nœud disponible
            best_node = next(
                (n for n in active_nodes if n.can_accept()), None
            )

        if best_node and best_node.can_accept():
            # act1 : controller_decision(t) := n
            self.controller_decision[task_id] = best_node.node_id
            self.audit_log.append({
                "event": "CONTROLLER_ASSIGN",
                "task": task_id,
                "node": best_node.node_id,
                "priority": priority
            })
            print(f"[CONTROLLER] Tâche {task_id} ({priority}) "
                  f"→ Nœud {best_node.node_id}")
            return best_node.node_id
        else:
            print(f"[ERREUR] Aucun nœud disponible pour {task_id}")
            return None

    def rpc_request(self, task_id):
        """
        RPC_REQUEST de R3 :
        - Envoie la requête RPC au nœud choisi par le contrôleur
        """
        if task_id not in self.controller_decision:
            print(f"[ERREUR] Pas de décision pour {task_id}")
            return False

        node_id = self.controller_decision[task_id]
        self.audit_log.append({
            "event": "RPC_REQUEST",
            "task": task_id,
            "node": node_id
        })
        print(f"[RPC_REQUEST] Envoi tâche {task_id} → Nœud {node_id}")
        return node_id

    def rpc_receive(self, task_id, node_id):
        """
        RPC_RECEIVE de R3 :
        - Le nœud reçoit la tâche et commence l'exécution
        """
        node = self.network.get_node(node_id)
        if node and node.assign_task(task_id):
            self.audit_log.append({
                "event": "RPC_RECEIVE",
                "task": task_id,
                "node": node_id
            })
            print(f"[RPC_RECEIVE] Tâche {task_id} assignée à Nœud {node_id}")
            return True
        return False

    def print_audit_log(self):
        print("\n=== Journal de traçabilité (audit_log) ===")
        for entry in self.audit_log:
            print(entry)