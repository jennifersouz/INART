import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import math
import time
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


### === LÓGICA DO ALGORITMO RRT 3D === ###

class Node:
    def __init__(self, x, y, z=0, name=None):
        self.x = x
        self.y = y
        self.z = z
        self.name = name
        self.parent = None

def load_csv(filename):
    nodes = {}
    node_name_map = {}
    node_coords = {}

    if not os.path.exists(filename):
        print(f"Erro: Arquivo '{filename}' não encontrado!")
        return None, None, None

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
                    node_coords[(x, y, z)] = origem
                if destino_norm not in node_name_map:
                    node_name_map[destino_norm] = destino
                    nodes[destino] = (x, y, z)
                    node_coords[(x, y, z)] = destino

        return nodes, node_name_map, node_coords

    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return None, None, None

def find_node_case_insensitive(nodes_dict, node_name_map, name):
    name_norm = name.lower()
    if name_norm in node_name_map:
        return nodes_dict[node_name_map[name_norm]]
    return None

def distance(node1, node2):
    return math.sqrt(
        (node1.x - node2.x)**2 +
        (node1.y - node2.y)**2 +
        (node1.z - node2.z)**2
    )

def steer(from_node, to_node, step_size):
    dist = distance(from_node, to_node)
    if dist <= step_size:
        return Node(to_node.x, to_node.y, to_node.z)
    else:
        dx = to_node.x - from_node.x
        dy = to_node.y - from_node.y
        dz = to_node.z - from_node.z
        scale = step_size / dist
        new_x = from_node.x + dx * scale
        new_y = from_node.y + dy * scale
        new_z = from_node.z + dz * scale
        return Node(new_x, new_y, new_z)

def rrt(start, goal, max_iter=5000, step_size=3.0, goal_sample_rate=0.2, return_stats=False):
    start_time = time.time()
    start_node = Node(*start, name="Start")
    goal_node = Node(*goal, name="Goal")
    tree = [start_node]

    x_range = (min(start[0], goal[0])-50, max(start[0], goal[0])+50)
    y_range = (min(start[1], goal[1])-50, max(start[1], goal[1])+50)
    z_range = (min(start[2], goal[2])-50, max(start[2], goal[2])+50)

    for iteration in range(max_iter):
        if np.random.random() < goal_sample_rate:
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

        new_node.parent = nearest
        tree.append(new_node)

        if distance(new_node, goal_node) < step_size * 2.0:
            goal_node.parent = new_node
            break

    path = []
    current = goal_node
    while current:
        path.append(current)
        current = current.parent
    path = path[::-1]

    execution_time = time.time() - start_time

    # Estatísticas
    peso_x = 2.0
    peso_y = 1.0
    peso_z = 1.0

    total_length = 0.0
    delta_x = 0.0
    delta_y = 0.0
    delta_z = 0.0

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
        f"Comprimento total (euclidiano): {total_length:.2f} ",
        f"Custo total ponderado: {custo_ponderado:.2f} ",
        f" - Portagem total: {delta_x:.2f}  (peso = {peso_x})",
        f" - Distancia total: {delta_y:.2f}  (peso = {peso_y})",
        f" - Gasolina total: {delta_z:.2f}  (peso = {peso_z})"
    ]

    if return_stats:
        return path, tree, stats
    return path, tree

def plot_result(tree, path, start, goal, start_name, goal_name):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    for node in tree:
        if node.parent:
            ax.plot([node.x, node.parent.x],
                    [node.y, node.parent.y],
                    [node.z, node.parent.z],
                    color='lightblue', linewidth=2.0)

    if path:
        path_x = [node.x for node in path]
        path_y = [node.y for node in path]
        path_z = [node.z for node in path]
        ax.plot(path_x, path_y, path_z, color='red', linewidth=2, label='Caminho final')

    ax.scatter(start[0], start[1], start[2], color='green', s=100, marker='o', label='Início')
    ax.scatter(goal[0], goal[1], goal[2], color='blue', s=100, marker='X', label='Objetivo')

    ax.text(start[0], start[1], start[2], f'{start_name}', color='green')
    ax.text(goal[0], goal[1], goal[2], f'{goal_name}', color='blue')

    ax.set_title("Resultado do RRT em 3D")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.legend()
    plt.show()

### === INTERFACE GRÁFICA COM TKINTER === ###

class RRTApp:
    def __init__(self, master):
        self.master = master
        self.master.title("RRT - Planeamento de Caminho")
        self.master.geometry("700x550")
        self.master.configure(bg="#f4f4f4")

        self.nodes_dict = {}
        self.node_name_map = {}

        self.create_widgets()

    def create_widgets(self):
        style_font = ("Segoe UI", 11)

        # === Título ===
        title_label = tk.Label(self.master, text="Planeamento com RRT 3D", font=("Segoe UI", 16, "bold"), bg="#f4f4f4",
                               fg="#2c3e50")
        title_label.pack(pady=10)

        # === Frame principal ===
        main_frame = tk.Frame(self.master, bg="#f4f4f4")
        main_frame.pack(pady=10)

        # === Botão de carregar CSV ===
        self.load_button = tk.Button(main_frame, text="📂 Carregar CSV", command=self.load_csv_file, font=style_font,
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
        self.run_button = tk.Button(self.master, text="▶Executar RRT", command=self.run_rrt,
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

    def load_csv_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            nodes_dict, name_map, _ = load_csv(file_path)
            if nodes_dict:
                self.nodes_dict = nodes_dict
                self.node_name_map = name_map
                nomes = list(nodes_dict.keys())
                self.start_combobox['values'] = nomes
                self.goal_combobox['values'] = nomes

                # Atualiza o label com o nome do ficheiro carregado
                filename = os.path.basename(file_path)
                self.current_file_label.config(
                    text=f"Ficheiro carregado: {filename}",
                    fg="#2c3e50",
                    font=("Segoe UI", 10, "bold")
                )
            else:
                self.current_file_label.config(text="Erro ao carregar ficheiro.", fg="red")
                messagebox.showerror("Erro", "Falha ao carregar o ficheiro CSV.")

    def run_rrt(self):
        start_name = self.start_combobox.get()
        goal_name = self.goal_combobox.get()

        if not start_name or not goal_name:
            messagebox.showwarning("Aviso", "Por favor, selecione os nós de origem e destino.")
            return

        start = find_node_case_insensitive(self.nodes_dict, self.node_name_map, start_name)
        goal = find_node_case_insensitive(self.nodes_dict, self.node_name_map, goal_name)

        if not start or not goal:
            messagebox.showerror("Erro", "Nó de origem ou destino inválido.")
            return

        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "Executando algoritmo RRT...\n")

        path, tree, stats = rrt(start, goal, return_stats=True)

        if path:
            self.stats_text.insert(tk.END, "\ncaminho encontrado!\n\n")
            for line in stats:
                self.stats_text.insert(tk.END, line + "\n")
            plot_result(tree, path, start, goal, start_name, goal_name)
        else:
            self.stats_text.insert(tk.END, "\nNenhum caminho encontrado.")


if __name__ == "__main__":
    root = tk.Tk()
    app = RRTApp(root)
    root.mainloop()
