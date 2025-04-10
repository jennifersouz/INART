#https://github.com/zhm-real/PathPlanning/blob/master/Sampling_based_Planning/rrt_2D/rrt_star.py
import csv
import matplotlib.pyplot as plt
import numpy as np
import math
import time
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class Node:
    def __init__(self, x, y, z=0, name=None):
        self.x = x
        self.y = y
        self.z = z
        self.name = name
        self.parent = None
        self.cost = float('inf')
        self.children = []

def load_csv(filename):
    nodes = {}
    node_name_map = {}
    if not os.path.exists(filename):
        return None, None

    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 5:
                    continue
                origem, destino, x, y, raio = row[:5]
                try:
                    x, y, z = float(x), float(y), float(raio)
                except ValueError:
                    continue
                origem_norm = origem.lower()
                destino_norm = destino.lower()
                if origem_norm not in node_name_map:
                    node_name_map[origem_norm] = origem
                    nodes[origem] = (x, y, z)
                if destino_norm not in node_name_map:
                    node_name_map[destino_norm] = destino
                    nodes[destino] = (x, y, z)
        return nodes, node_name_map
    except Exception as e:
        print(f"Erro ao ler CSV: {e}")
        return None, None

def find_node_case_insensitive(nodes_dict, node_name_map, name):
    name_norm = name.lower()
    if name_norm in node_name_map:
        return nodes_dict[node_name_map[name_norm]]
    return None

def distance(node1, node2):
    return math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2 + (node1.z - node2.z)**2)

def steer(from_node, to_node, step_size):
    dist = distance(from_node, to_node)
    if dist <= step_size:
        return Node(to_node.x, to_node.y, to_node.z)
    else:
        dx = to_node.x - from_node.x
        dy = to_node.y - from_node.y
        dz = to_node.z - from_node.z
        scale = step_size / dist
        return Node(from_node.x + dx * scale, from_node.y + dy * scale, from_node.z + dz * scale)

def rrt_star(start_coords, goal_coords, max_iter=500, step_size=1.0, goal_sample_rate=0.2):
    start_time = time.time()
    start_node = Node(*start_coords, name="Start")
    start_node.cost = 0
    goal_node = Node(*goal_coords, name="Goal")

    tree = [start_node]
    explored_nodes = []
    last_improvement = 0

    x_range = (min(start_coords[0], goal_coords[0])-50, max(start_coords[0], goal_coords[0])+50)
    y_range = (min(start_coords[1], goal_coords[1])-50, max(start_coords[1], goal_coords[1])+50)
    z_range = (min(start_coords[2], goal_coords[2])-50, max(start_coords[2], goal_coords[2])+50)

    best_goal_node = None
    best_goal_cost = float('inf')

    for iteration in range(max_iter):
        if best_goal_node and iteration > max_iter * 0.7:
            rand_node = goal_node
        elif best_goal_node and np.random.random() < 0.1:
            path_nodes = []
            current = best_goal_node
            while current:
                path_nodes.append(current)
                current = current.parent
            selected_node = np.random.choice(path_nodes)
            rand_x = selected_node.x + np.random.normal(0, step_size/2)
            rand_y = selected_node.y + np.random.normal(0, step_size/2)
            rand_z = selected_node.z + np.random.normal(0, step_size/2)
            rand_node = Node(rand_x, rand_y, rand_z)
        elif np.random.random() < goal_sample_rate:
            rand_node = goal_node
        else:
            rand_x = np.random.uniform(x_range[0], x_range[1])
            rand_y = np.random.uniform(y_range[0], y_range[1])
            rand_z = np.random.uniform(z_range[0], z_range[1])
            rand_node = Node(rand_x, rand_y, rand_z)

        nearest = min(tree, key=lambda node: distance(node, rand_node))
        new_node = steer(nearest, rand_node, step_size)

        if any(distance(node, new_node) < step_size/10 for node in tree):
            continue

        neighbor_radius = min(15.0 * math.sqrt(math.log(len(tree)+1) / (len(tree)+1)), step_size * 5)
        neighbors = [node for node in tree if distance(node, new_node) < neighbor_radius]

        min_cost = nearest.cost + distance(nearest, new_node)
        best_parent = nearest

        for neighbor in neighbors:
            potential_cost = neighbor.cost + distance(neighbor, new_node)
            if potential_cost < min_cost:
                min_cost = potential_cost
                best_parent = neighbor

        new_node.parent = best_parent
        new_node.cost = min_cost
        best_parent.children.append(new_node)
        tree.append(new_node)
        explored_nodes.append((new_node.x, new_node.y))

        for neighbor in neighbors:
            if neighbor != best_parent:
                potential_cost = new_node.cost + distance(new_node, neighbor)
                if potential_cost < neighbor.cost:
                    if neighbor.parent:
                        neighbor.parent.children.remove(neighbor)
                    neighbor.parent = new_node
                    neighbor.cost = potential_cost
                    new_node.children.append(neighbor)

        if distance(new_node, goal_node) < step_size * 2.0:
            potential_goal_cost = new_node.cost + distance(new_node, goal_node)
            if potential_goal_cost < best_goal_cost:
                goal_node.parent = new_node
                goal_node.cost = potential_goal_cost
                best_goal_node = goal_node
                best_goal_cost = potential_goal_cost
                last_improvement = iteration

            if (iteration - last_improvement) > 500 and best_goal_node:
                break

    if best_goal_node:
        path = []
        current = best_goal_node
        while current:
            path.append(current)
            current = current.parent
        path.reverse()

        execution_time = time.time() - start_time

        # Estatísticas detalhadas
        peso_x = 2.0
        peso_y = 1.0
        peso_z = 1.0

        delta_x = delta_y = delta_z = total_length = 0.0

        for i in range(1, len(path)):
            dx = abs(path[i].x - path[i - 1].x)
            dy = abs(path[i].y - path[i - 1].y)
            dz = abs(path[i].z - path[i - 1].z)
            delta_x += dx
            delta_y += dy
            delta_z += dz
            total_length += math.sqrt(dx**2 + dy**2 + dz**2)

        custo_ponderado = delta_x * peso_x + delta_y * peso_y + delta_z * peso_z

        stats = [
            f"Tempo de execução: {execution_time:.4f} segundos",
            f"Nós no caminho: {len(path)}",
            f"Nós totais gerados: {len(tree)}",
            f"Comprimento total (euclidiano): {total_length:.2f}",
            f"Custo total ponderado: {custo_ponderado:.2f} ",
            f" - Portagem total: {delta_x* 2:.2f}  (peso = {peso_x})",
            f" - Distancia total: {delta_y:.2f}  (peso = {peso_y})",
            f" - Gasolina total: {delta_z:.2f}  (peso = {peso_z})"
        ]

        return path, tree, explored_nodes, stats
    else:
        return None, tree, explored_nodes, ["Nenhum caminho encontrado."]

def plot_result(tree, path, explored_nodes, start, goal, start_name, goal_name):
    fig, ax = plt.subplots(figsize=(10, 10))

    # 1. Nós explorados com transparência
    if explored_nodes:
        ex_x, ex_y = zip(*explored_nodes)
        ax.scatter(ex_x, ex_y, color='gray', s=8, alpha=0.1, label='Nós explorados')

    # 2. Arestas da árvore (light blue)
    for node in tree:
        if node.parent:
            ax.plot([node.x, node.parent.x], [node.y, node.parent.y], color='lightblue', linewidth=0.4)

    # 3. Caminho final em vermelho destacado
    if path:
        path_x = [node.x for node in path]
        path_y = [node.y for node in path]
        ax.plot(path_x, path_y, color='red', linewidth=3, label='Caminho final')

    # 4. Início e objetivo com destaque
    ax.scatter(start[0], start[1], color='green', edgecolors='black', s=120, marker='o', zorder=5, label='Início')
    ax.scatter(goal[0], goal[1], color='blue', edgecolors='black', s=120, marker='X', zorder=5, label='Objetivo')

    # 5. Rótulos dos pontos com leve deslocamento
    ax.text(start[0], start[1]+2, start_name, fontsize=12, color='green', weight='bold', ha='center', va='bottom')
    ax.text(goal[0], goal[1]+2, goal_name, fontsize=12, color='blue', weight='bold', ha='center', va='bottom')


    # 6. Estética geral
    ax.set_title("Resultado do RRT*", fontsize=14, weight='bold')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()
    ax.grid(True)
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

class RRTStarApp:
    def __init__(self, master):
        self.master = master
        self.master.title("RRT* - Planeamento de Caminho")
        self.master.geometry("700x500")
        self.master.configure(bg="#f4f4f4")
        self.nodes_dict = {}
        self.node_name_map = {}
        self.create_widgets()

    def create_widgets(self):
        style_font = ("Segoe UI", 11)

        # === Título ===
        title_label = tk.Label(self.master, text="Planeamento com RRT* 2D", font=("Segoe UI", 16, "bold"), bg="#f4f4f4",
                               fg="#2c3e50")
        title_label.pack(pady=10)

        # === Frame principal ===
        main_frame = tk.Frame(self.master, bg="#f4f4f4")
        main_frame.pack(pady=10)

        # === Botão de carregar CSV ===
        self.load_button = tk.Button(main_frame, text="📂 Carregar CSV", command=self.load_csv, font=style_font,
                                     bg="#3498db", fg="white", relief="flat", padx=10, pady=5)
        self.load_button.grid(row=0, column=0, columnspan=2, pady=10)

        # === Label para mostrar nome do CSV ===
        self.current_file_label = tk.Label(self.master, text="📁 Nenhum ficheiro carregado",
                                           font=("Segoe UI", 10, "italic"), fg="#7f8c8d", bg="#f4f4f4")
        self.current_file_label.pack(pady=(0, 10))

        # === Combobox de origem ===
        self.start_label = tk.Label(main_frame, text="Nó de origem:", font=style_font, bg="#f4f4f4")
        self.start_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.start_combobox = ttk.Combobox(main_frame, state="readonly", font=style_font, width=30)
        self.start_combobox.grid(row=1, column=1, pady=5)

        # === Combobox de destino ===
        self.goal_label = tk.Label(main_frame, text="Nó de destino:", font=style_font, bg="#f4f4f4")
        self.goal_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.goal_combobox = ttk.Combobox(main_frame, state="readonly", font=style_font, width=30)
        self.goal_combobox.grid(row=2, column=1, pady=5)

        # === Botão Executar ===
        self.run_button = tk.Button(self.master, text="▶Executar RRT*", command=self.run_rrt_star,
                                    font=("Segoe UI", 12, "bold"), bg="#27ae60", fg="white", relief="flat", padx=12,
                                    pady=6)
        self.run_button.pack(pady=20)

        # === Frame das estatísticas ===
        stats_frame = tk.LabelFrame(self.master, text="Estatísticas do Caminho", font=("Segoe UI", 12, "bold"),
                                    bg="#fdfdfd", fg="#2c3e50", padx=10, pady=10, bd=2, relief="groove")
        stats_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.stats_text = tk.Text(stats_frame, height=12, font=("Consolas", 10), wrap="word", bg="#ffffff",
                                  fg="#2c3e50", relief="flat", bd=0)
        self.stats_text.pack(fill="both", expand=True)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            nodes, name_map = load_csv(file_path)
            if nodes:
                self.nodes_dict = nodes
                self.node_name_map = name_map
                nomes = list(nodes.keys())
                self.start_combobox["values"] = nomes
                self.goal_combobox["values"] = nomes
                filename = os.path.basename(file_path)
                self.current_file_label.config(text=f"📄 Ficheiro carregado: {filename}", fg="#2c3e50")
                messagebox.showinfo("Sucesso", f"{len(nomes)} nós carregados com sucesso.")
            else:
                messagebox.showerror("Erro", "Erro ao carregar CSV.")

    def run_rrt_star(self):
        self.stats_text.delete(1.0, tk.END)
        start_name = self.start_combobox.get()
        goal_name = self.goal_combobox.get()

        if not start_name or not goal_name:
            messagebox.showwarning("Atenção", "Seleciona origem e destino.")
            return

        start = find_node_case_insensitive(self.nodes_dict, self.node_name_map, start_name)
        goal = find_node_case_insensitive(self.nodes_dict, self.node_name_map, goal_name)

        if not start or not goal:
            messagebox.showerror("Erro", "Nó de origem ou destino inválido.")
            return

        path, tree, explored, stats = rrt_star(start, goal)
        for line in stats:
            self.stats_text.insert(tk.END, line + "\n")

        if path:
            plot_result(tree, path, explored, start, goal, start_name, goal_name)

if __name__ == "__main__":
    root = tk.Tk()
    app = RRTStarApp(root)
    root.mainloop()