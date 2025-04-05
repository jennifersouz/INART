import csv
import matplotlib.pyplot as plt
import numpy as np
import math
import time
import os
import networkx as nx
from matplotlib.patches import Circle

class Node:
    def __init__(self, x, y, name=None):
        self.x = x
        self.y = y
        self.name = name  # Nome do nó (opcional)
        self.parent = None
        self.cost = float('inf')
        self.children = []

def load_csv(filename):
    """Carrega os dados do arquivo CSV"""
    nodes = {}
    node_name_map = {}  # Mapeamento de nomes normalizados para nomes originais
    node_coords = {}    # Mapeamento de coordenadas para nomes
    
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
                    x, y = float(x), float(y)
                except ValueError:
                    continue
                
                # Normalização de nomes para busca case-insensitive
                origem_norm = origem.lower()
                destino_norm = destino.lower()
                
                if origem_norm not in node_name_map:
                    node_name_map[origem_norm] = origem
                    nodes[origem] = (x, y)
                    node_coords[(x, y)] = origem
                if destino_norm not in node_name_map:
                    node_name_map[destino_norm] = destino
                    nodes[destino] = (x, y)
                    node_coords[(x, y)] = destino
                
        return nodes, node_name_map, node_coords
    
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return None, None, None

def find_node_case_insensitive(nodes_dict, node_name_map, name):
    """Encontra um nó pelo nome, ignorando maiúsculas e minúsculas"""
    name_norm = name.lower()
    if name_norm in node_name_map:
        return nodes_dict[node_name_map[name_norm]]
    return None

def distance(node1, node2):
    """Calcula a distância euclidiana entre dois nós"""
    return math.hypot(node1.x - node2.x, node1.y - node2.y)

def steer(from_node, to_node, step_size):
    """Cria um novo nó na direção do nó alvo"""
    dist = distance(from_node, to_node)
    if dist <= step_size:
        return to_node
    else:
        theta = math.atan2(to_node.y - from_node.y, to_node.x - from_node.x)
        new_x = from_node.x + step_size * math.cos(theta)
        new_y = from_node.y + step_size * math.sin(theta)
        return Node(new_x, new_y)

def rrt_star(start, goal, max_iter=5000, step_size=3.0, goal_sample_rate=0.2):
    """Implementação do algoritmo RRT* sem obstáculos"""
    start_time = time.time()
    start_node = Node(*start, name="Start")
    start_node.cost = 0
    goal_node = Node(*goal, name="Goal")
    
    tree = [start_node]
    explored_nodes = []
    
    # Defina limites do espaço de busca
    x_range = (min(start[0], goal[0])-50, max(start[0], goal[0])+50)
    y_range = (min(start[1], goal[1])-50, max(start[1], goal[1])+50)
    
    best_goal_node = None
    best_goal_cost = float('inf')
    
    for iteration in range(max_iter):
        # Amostragem com viés para o objetivo
        if best_goal_node and iteration > max_iter * 0.7:
            # Se já encontramos um caminho e estamos na fase final, concentre em otimizar
            rand_node = goal_node
        elif best_goal_node and np.random.random() < 0.1:
            # Amostragem ao longo do melhor caminho atual para refinamento
            path_nodes = []
            current = best_goal_node
            while current:
                path_nodes.append(current)
                current = current.parent
            
            selected_node = np.random.choice(path_nodes)
            rand_x = selected_node.x + np.random.normal(0, step_size/2)
            rand_y = selected_node.y + np.random.normal(0, step_size/2)
            rand_node = Node(rand_x, rand_y)
        elif np.random.random() < goal_sample_rate:
            rand_node = goal_node
        else:
            rand_x = np.random.uniform(x_range[0], x_range[1])
            rand_y = np.random.uniform(y_range[0], y_range[1])
            rand_node = Node(rand_x, rand_y)
        
        # Encontrar nó mais próximo
        nearest = min(tree, key=lambda node: distance(node, rand_node))
        new_node = steer(nearest, rand_node, step_size)
        
        # Verificar se o nó já existe aproximadamente
        if any(distance(node, new_node) < step_size/10 for node in tree):
            continue
            
        # Encontrar vizinhos para rewiring
        neighbor_radius = min(15.0 * math.sqrt(math.log(len(tree)+1) / (len(tree)+1)), step_size * 5)
        neighbors = [node for node in tree if distance(node, new_node) < neighbor_radius]
        
        # Escolher melhor pai
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
        
        # Rewiring
        for neighbor in neighbors:
            if neighbor != best_parent:
                potential_cost = new_node.cost + distance(new_node, neighbor)
                if potential_cost < neighbor.cost:
                    if neighbor.parent:
                        neighbor.parent.children.remove(neighbor)
                    neighbor.parent = new_node
                    neighbor.cost = potential_cost
                    new_node.children.append(neighbor)
        
        # Verificar se alcançou o objetivo
        dist_to_goal = distance(new_node, goal_node)
        if dist_to_goal < step_size * 2.0:
            potential_goal_cost = new_node.cost + dist_to_goal
            
            if potential_goal_cost < best_goal_cost:
                goal_node.parent = new_node
                goal_node.cost = potential_goal_cost
                best_goal_node = goal_node
                best_goal_cost = potential_goal_cost
                
                # Se encontramos um caminho muito bom, podemos encerrar
                if iteration > max_iter * 0.8 and len(tree) > 1000:
                    break
    
    # Recuperar o melhor caminho
    if best_goal_node:
        path = []
        current = best_goal_node
        while current:
            path.append(current)
            current = current.parent
        
        path = path[::-1]
        execution_time = time.time() - start_time
        print(f"\nTempo de execução: {execution_time:.2f} segundos")
        print(f"Custo total do caminho: {best_goal_cost:.2f}")
        
        return path, tree, explored_nodes
    
    print("\nNão foi possível encontrar um caminho dentro do número máximo de iterações.")
    print(f"Tempo de execução: {time.time() - start_time:.2f} segundos")
    return None, tree, explored_nodes

def plot_result(tree, path, explored_nodes, start, goal, start_name, goal_name):
    """Desenha o resultado do RRT* em 2D"""
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Plotar nós explorados
    if explored_nodes:
        ex_x, ex_y = zip(*explored_nodes)
        ax.scatter(ex_x, ex_y, color='gray', s=10, label='Nós explorados')
    
    # Plotar arestas da árvore
    for node in tree:
        if node.parent:
            ax.plot([node.x, node.parent.x], [node.y, node.parent.y], color='lightblue', linewidth=0.5)

    # Plotar caminho final
    if path:
        path_x = [node.x for node in path]
        path_y = [node.y for node in path]
        ax.plot(path_x, path_y, color='red', linewidth=2, label='Caminho final')

    # Plotar início e objetivo com nomes fornecidos
    ax.scatter(start[0], start[1], color='green', s=100, marker='o', label='Início')
    ax.scatter(goal[0], goal[1], color='blue', s=100, marker='X', label='Objetivo')

    # Adicionar rótulos com os nomes reais dos nós
    ax.text(start[0], start[1], f'  {start_name}', fontsize=12, verticalalignment='bottom', color='green', weight='bold')
    ax.text(goal[0], goal[1], f'  {goal_name}', fontsize=12, verticalalignment='bottom', color='blue', weight='bold')

    ax.set_title("Resultado do RRT*")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()
    ax.grid(True)
    plt.axis('equal')
    plt.show()



# Função auxiliar para calcular distância entre nós
def distance(node1, node2):
    """Calcula a distância euclidiana entre dois nós"""
    return ((node1.x - node2.x)**2 + (node1.y - node2.y)**2)**0.5

def main():
    """Função principal para execução interativa"""
    print("=== Planejamento de Caminho com RRT* ===")
    
    # Carregar dados do CSV
    filename = input("Digite o nome do arquivo CSV (ex: grafo.csv): ").strip()
    nodes_dict, node_name_map, node_coords = load_csv(filename)
    
    if nodes_dict is None:
        return
    
    print(f"\nGrafo carregado com sucesso!")
    print(f"- Número de nós: {len(nodes_dict)}")
    print(f"- Nós disponíveis: {', '.join(nodes_dict.keys())}")
    
    # Selecionar nós de início e objetivo
    while True:
        start_name = input("\nDigite o nó de origem: ").strip()
        start = find_node_case_insensitive(nodes_dict, node_name_map, start_name)
        if start:
            break
        print("Nó não encontrado. Tente novamente.")
    
    while True:
        goal_name = input("Digite o nó de destino: ").strip()
        goal = find_node_case_insensitive(nodes_dict, node_name_map, goal_name)
        if goal:
            break
        print("Nó não encontrado. Tente novamente.")
    
    # Executar algoritmo com valores padrão
    print("\nExecutando algoritmo RRT*...")
    path, tree, explored = rrt_star(start, goal)
    plot_result(tree, path, explored, start, goal, start_name, goal_name)


if __name__ == "__main__":
    main()