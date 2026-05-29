# main.py
# Programme principal - Simulation du délestage collaboratif
# avec le dataset PTB-XL et le modèle Event-B R3

import pandas as pd
import random
from fog_nodes import FogNetwork
from controller import FogController

# ============================================================
# 1. Chargement du dataset PTB-XL
# ============================================================
def load_ptbxl(filepath="ptbxl_database.csv", n_samples=10):
    """
    Charge les enregistrements ECG du dataset PTB-XL
    Correspond à ECG_RECORDS et PATIENTS de C0
    """
    df = pd.read_csv(filepath)
    # Sélectionner n_samples enregistrements
    sample = df.head(n_samples)
    ecg_tasks = []
    for _, row in sample.iterrows():
        ecg_tasks.append({
            "task_id":    f"T{row['ecg_id']}",
            "patient_id": f"P{row['patient_id']}",
            "ecg_id":     row['ecg_id'],
            "priority":   "critical",    # toutes les tâches ECG sont critical
            "integrity":  True,          # task_integrity de R3
            "confidentiality": True      # task_confidentiality de R3
        })
    return ecg_tasks

# ============================================================
# 2. Simulation ADD_ECG_TASK
# ============================================================
def add_ecg_tasks(ecg_tasks):
    """
    ADD_ECG_TASK de R3 :
    - Ajoute les tâches ECG dans pending_tasks
    - Priorité forcée à critical
    """
    pending_tasks = {}
    task_state = {}
    print("\n=== ADD_ECG_TASK ===")
    for task in ecg_tasks:
        tid = task["task_id"]
        pending_tasks[tid] = task
        task_state[tid] = "waiting"     # task_state(t) := waiting
        print(f"[ADD_ECG_TASK] {tid} | Patient: {task['patient_id']} "
              f"| Priorité: {task['priority']}")
    return pending_tasks, task_state

# ============================================================
# 3. Simulation NODE_FAILURE
# ============================================================
def simulate_node_failure(network, controller, task_state, pending_tasks):
    """
    NODE_FAILURE de R3 :
    - Simule la panne d'un nœud
    - Récupère les tâches et les remet en waiting
    """
    active = network.get_active_nodes()
    if not active:
        return

    # Choisir un nœud aléatoire pour la panne
    failed_node = random.choice(active)
    print(f"\n[NODE_FAILURE] Panne du nœud {failed_node.node_id} !")

    # Récupérer les tâches échouées
    failed_tasks = failed_node.simulate_failure()

    for tid in failed_tasks:
        # act : task_state(t) := waiting
        task_state[tid] = "waiting"
        # act : pending_tasks := pending_tasks ∪ failed_tasks
        pending_tasks[tid] = {"task_id": tid, "priority": "critical"}
        print(f"[NODE_FAILURE] Tâche {tid} remise en waiting")

# ============================================================
# 4. Programme principal
# ============================================================
def main():
    print("=" * 55)
    print("  Simulation Fog Computing - Délestage ECG PTB-XL")
    print("=" * 55)

    # Initialisation du réseau Fog
    # NODES = 3 nœuds, max_load = 5
    network = FogNetwork(num_nodes=3, capacity=5)
    controller = FogController(network)
    network.print_status()

    # Chargement des tâches ECG depuis PTB-XL
    ecg_tasks = load_ptbxl("ptbxl_database.csv", n_samples=5)
    pending_tasks, task_state = add_ecg_tasks(ecg_tasks)

    # Traitement des tâches
    print("\n=== Traitement des tâches ECG ===")
    completed_tasks = []

    for tid, task in pending_tasks.items():
        print(f"\n--- Traitement de {tid} ---")

        # CONTROLLER_ASSIGN : choisir le meilleur nœud
        node_id = controller.assign_node(tid, task["priority"])
        if not node_id:
            continue

        # RPC_REQUEST : envoyer la requête
        node_id = controller.rpc_request(tid)
        if not node_id:
            continue

        # RPC_RECEIVE : assigner la tâche au nœud
        success = controller.rpc_receive(tid, node_id)
        if success:
            task_state[tid] = "running"

            # COMPLETE_TASK : finaliser la tâche
            node = network.get_node(node_id)
            if node.complete_task(tid):
                task_state[tid] = "completed"
                completed_tasks.append(tid)
                print(f"[COMPLETE_TASK] {tid} terminée sur Nœud {node_id}")

    # Simulation d'une panne
    print("\n=== Simulation de panne ===")
    simulate_node_failure(network, controller, task_state, pending_tasks)

    # Résultats finaux
    print("\n=== Résultats finaux ===")
    network.print_status()
    print(f"\nTâches complétées : {completed_tasks}")
    print(f"États des tâches  : {task_state}")
    controller.print_audit_log()

if __name__ == "__main__":
    main()