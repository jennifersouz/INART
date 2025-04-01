import csv
import matplotlib.pyplot as plt
import numpy as np
import random
import math
from matplotlib.patches import Circle
from scipy.spatial import KDTree
import time
import os

class Node:
    def __init__(self, x, y, name=None):
        self.x = x
        self.y = y
        self.name = name  # Nome do nó (opcional)
        self.parent = None
        self.cost = float('inf')
        self.children = []

def load_csv(filename):
    """Carrega os dados do arquivo CSV e define obstáculos de forma mais eficiente"""
    nodes = {}
    obstacles = []
    
    if not os.path.exists(filename):
        print(f"Erro: Arquivo '{filename}' não encontrado!")
        return None, None
    
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 5:
                    continue
                
                origem, destino, x, y, raio = row[:5]
                try:
                    x, y, raio = float(x), float(y), float(raio)
                except ValueError:
                    continue
                
                if origem not in nodes:
                    nodes[origem] = (x, y)
                if destino not in nodes:
                    nodes[destino] = (x, y)
                
        # Gerar obstáculos aleatórios no espaço, evitando sobreposição
        num_obstacles = 5  # Ajuste conforme necessário
        min_radius, max_radius = 3.0, 8.0
        margin = 5.0
        
        x_values = [coord[0] for coord in nodes.values()]
        y_values = [coord[1] for coord in nodes.values()]
        
        x_min, x_max = min(x_values) - 20, max(x_values) + 20
        y_min, y_max = min(y_values) - 20, max(y_values) + 20
        
        while len(obstacles) < num_obstacles:
            obs_x = random.uniform(x_min, x_max)
            obs_y = random.uniform(y_min, y_max)
            obs_radius = random.uniform(min_radius, max_radius)
            
            # Garantir que os obstáculos não bloqueiam o início ou objetivo
            inicio = list(nodes.values())[0] if nodes else None
            objetivo = list(nodes.values())[-1] if nodes else None
            
            if inicio and math.hypot(obs_x - inicio[0], obs_y - inicio[1]) < obs_radius + margin:
                continue
            if objetivo and math.hypot(obs_x - objetivo[0], obs_y - objetivo[1]) < obs_radius + margin:
                continue
            
            # Evitar sobreposição de obstáculos
            if not any(math.hypot(obs_x - ox, obs_y - oy) < (r + obs_radius + margin) for ox, oy, r in obstacles):
                obstacles.append((obs_x, obs_y, obs_radius))
                
        return nodes, obstacles
    
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return None, None



def distance(node1, node2):
    """Calcula a distância euclidiana entre dois nós"""
    return math.hypot(node1.x - node2.x, node1.y - node2.y)

def is_collision_free(new_node, obstacles, margin=0.5):
    """Verifica se um nó está livre de colisões"""
    for (ox, oy, r) in obstacles:
        if math.hypot(new_node.x - ox, new_node.y - oy) < (r + margin):
            return False
    return True

def check_path_collision(start, end, obstacles, margin=0.5, num_points=10):
    """Verifica colisão ao longo de um caminho"""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dist = math.hypot(dx, dy)
    
    if dist == 0:
        return True
        
    dx /= dist
    dy /= dist
    
    for i in range(num_points + 1):
        t = i / num_points
        x = start[0] + t * dx * dist
        y = start[1] + t * dy * dist
        if not is_collision_free(Node(x, y), obstacles, margin):
            return False
    return True

def rrt_star(start, goal, obstacles, max_iter=5000, step_size=3.0, goal_sample_rate=0.2):
    """Implementação do algoritmo RRT*"""
    start_time = time.time()
    start_node = Node(*start, name="Start")
    start_node.cost = 0
    goal_node = Node(*goal, name="Goal")
    
    tree = [start_node]
    explored_nodes = []
    
    for iteration in range(max_iter):
        # Amostragem com viés para o objetivo
        if random.random() < goal_sample_rate:
            rand_node = goal_node
        else:
            rand_x = random.uniform(min(start[0], goal[0])-50, max(start[0], goal[0])+50)
            rand_y = random.uniform(min(start[1], goal[1])-50, max(start[1], goal[1])+50)
            rand_node = Node(rand_x, rand_y)
        
        # Encontrar nó mais próximo
        nearest = min(tree, key=lambda node: distance(node, rand_node))
        new_node = steer(nearest, rand_node, step_size)
        
        # Verificar colisões
        if not (is_collision_free(new_node, obstacles) and 
                check_path_collision((nearest.x, nearest.y), (new_node.x, new_node.y), obstacles)):
            continue
        
        # Encontrar vizinhos para rewiring
        neighbor_radius = 15.0 * math.sqrt(math.log(len(tree)+1) / (len(tree)+1))
        neighbors = [node for node in tree if distance(node, new_node) < neighbor_radius 
                     and check_path_collision((node.x, node.y), (new_node.x, new_node.y), obstacles)]
        
        # Escolher melhor pai
        min_cost = nearest.cost + distance(nearest, new_node)
        best_parent = nearest
        
        for neighbor in neighbors:
            if neighbor.cost + distance(neighbor, new_node) < min_cost:
                min_cost = neighbor.cost + distance(neighbor, new_node)
                best_parent = neighbor
        
        new_node.parent = best_parent
        new_node.cost = min_cost
        best_parent.children.append(new_node)
        tree.append(new_node)
        explored_nodes.append((new_node.x, new_node.y))
        
        # Rewiring
        for neighbor in neighbors:
            if neighbor != best_parent and new_node.cost + distance(new_node, neighbor) < neighbor.cost:
                if neighbor.parent:
                    neighbor.parent.children.remove(neighbor)
                neighbor.parent = new_node
                neighbor.cost = new_node.cost + distance(new_node, neighbor)
                new_node.children.append(neighbor)
        
        # Verificar se alcançou o objetivo
        if distance(new_node, goal_node) < step_size * 1.5:
            if check_path_collision((new_node.x, new_node.y), goal, obstacles):
                goal_node.parent = new_node
                goal_node.cost = new_node.cost + distance(new_node, goal_node)
                
                path = []
                current = goal_node
                while current:
                    path.append(current)
                    current = current.parent
                
                path = path[::-1]
                print(f"\nEstatísticas do Caminho:")
                print(f"- Tempo de execução: {time.time() - start_time:.2f} segundos")
                print(f"- Número de iterações: {iteration}")
                print(f"- Custo total do caminho: {goal_node.cost:.2f}")
                print(f"- Número de nós no caminho: {len(path)}")
                print(f"- Comprimento do caminho: {sum(distance(path[i], path[i+1]) for i in range(len(path)-1)):.2f}")
                
                return path, tree, explored_nodes
    
    print("\nNão foi possível encontrar um caminho dentro do número máximo de iterações.")
    print(f"Tempo de execução: {time.time() - start_time:.2f} segundos")
    return None, tree, explored_nodes

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

def enhanced_plot(start, goal, obstacles, path=None, tree=None, explored=None, nodes_dict=None):
    """Visualização aprimorada do RRT*"""
    plt.figure(figsize=(12, 12))
    ax = plt.gca()
    
    # Configurações do gráfico
    ax.set_xlim(min(start[0], goal[0])-20, max(start[0], goal[0])+20)
    ax.set_ylim(min(start[1], goal[1])-20, max(start[1], goal[1])+20)
    ax.set_xlabel('Coordenada X', fontsize=12)
    ax.set_ylabel('Coordenada Y', fontsize=12)
    ax.set_title('Planejamento de Caminho com RRT*', fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Desenhar obstáculos
    for (x, y, r) in obstacles:
        obstacle = Circle((x, y), r, color='salmon', alpha=0.6, label='Obstáculos' if (x,y,r) == obstacles[0] else "")
        ax.add_patch(obstacle)
    
    # Desenhar árvore de exploração
    if tree:
        for node in tree:
            if node.parent:
                ax.plot([node.x, node.parent.x], [node.y, node.parent.y], 
                        color='lightblue', linewidth=0.5, alpha=0.4,
                        label='Árvore de exploração' if node == tree[1] else "")
    
    # Desenhar nós do grafo (se fornecido)
    if nodes_dict:
        for name, (x, y) in nodes_dict.items():
            ax.scatter(x, y, color='purple', s=30, alpha=0.7)
            ax.annotate(name, (x, y), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)
    
    # Desenhar nós explorados
    if explored:
        ex_x, ex_y = zip(*explored)
        ax.scatter(ex_x, ex_y, color='lightgray', s=5, alpha=0.3, label='Nós explorados')
    
    # Desenhar caminho encontrado
    if path:
        path_x = [node.x for node in path]
        path_y = [node.y for node in path]
        ax.plot(path_x, path_y, 'limegreen', linewidth=3, marker='o', 
                markersize=6, markerfacecolor='yellow', label='Caminho ótimo')
        
        # Anotar custo acumulado em cada ponto do caminho
        for i, node in enumerate(path):
            if i > 0:  # Ignora o nó inicial
                ax.annotate(f'{node.cost:.1f}', (node.x, node.y), 
                           textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
    
    # Marcar início e objetivo
    ax.scatter(start[0], start[1], color='darkgreen', s=200, 
               marker='s', edgecolor='black', label='Início')
    ax.scatter(goal[0], goal[1], color='darkblue', s=200, 
               marker='*', edgecolor='black', label='Objetivo')
    
    # Configurar legenda
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=10)
    
    plt.tight_layout()
    plt.show()

def main():
    """Função principal para execução interativa"""
    print("=== Planejamento de Caminho com RRT* ===")
    
    # Carregar dados do CSV
    filename = input("Digite o nome do arquivo CSV (ex: grafo.csv): ").strip()
    nodes_dict, obstacles = load_csv(filename)
    
    if nodes_dict is None or obstacles is None:
        return
    
    print(f"\nGrafo carregado com sucesso!")
    print(f"- Número de nós: {len(nodes_dict)}")
    print(f"- Número de obstáculos: {len(obstacles)}")
    print(f"- Nós disponíveis: {', '.join(nodes_dict.keys())}")
    
    # Selecionar nós de início e objetivo
    while True:
        start_name = input("\nDigite o nó de origem: ").strip()
        if start_name in nodes_dict:
            start = nodes_dict[start_name]
            break
        print("Nó não encontrado. Tente novamente.")
    
    while True:
        goal_name = input("Digite o nó de destino: ").strip()
        if goal_name in nodes_dict:
            goal = nodes_dict[goal_name]
            break
        print("Nó não encontrado. Tente novamente.")
    
    max_iter = 5000  # Número máximo de iterações fixo
    step_size = 3.0  # Tamanho do passo fixo
    goal_bias = 0.2  # Viés para o objetivo fixo

    # Executar algoritmo
    print("\nExecutando algoritmo RRT*...")
    path, tree, explored = rrt_star(start, goal, obstacles, 
                                  max_iter=max_iter, 
                                  step_size=step_size, 
                                  goal_sample_rate=goal_bias)
    
    # Visualizar resultados
    enhanced_plot(start, goal, obstacles, path, tree, explored, nodes_dict)
    
    # Salvar figura
    save = input("\nDeseja salvar o gráfico? (s/n): ").strip().lower()
    if save == 's':
        plt.savefig('rrt_star_path.png', dpi=300, bbox_inches='tight')
        print("Gráfico salvo como 'rrt_star_path.png'")

if __name__ == "__main__":
    main()