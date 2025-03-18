import numpy as np
import matplotlib.pyplot as plt
import random

class Node:
    """Representa um nó no grafo."""
    def __init__(self, name, x, y):
        self.name = name  # Nome do nó
        self.x = x  # Posição x
        self.y = y  # Posição y
        self.parent = None  # Nó pai

class RRTStar:
    """Implementação do algoritmo RRT* para o grafo de 8 nós."""
    def __init__(self, start, goal, graph, step_size=10, max_iter=500, radius=15):
        self.start = Node(*start)
        self.goal = Node(*goal)
        self.graph = graph
        self.step_size = step_size
        self.max_iter = max_iter
        self.radius = radius
        self.nodes = [self.start]

    def distance(self, node1, node2):
        """Calcula a distância euclidiana entre dois nós."""
        return np.hypot(node1.x - node2.x, node1.y - node2.y)

    def nearest_node(self, random_node):
        """Encontra o nó mais próximo do novo nó aleatório."""
        return min(self.nodes, key=lambda node: self.distance(node, random_node))

    def steer(self, from_node, to_node):
        """Move um nó na direção do nó alvo em passos definidos."""
        theta = np.arctan2(to_node.y - from_node.y, to_node.x - from_node.x)
        new_x = from_node.x + self.step_size * np.cos(theta)
        new_y = from_node.y + self.step_size * np.sin(theta)
        return Node(from_node.name, new_x, new_y)

    def find_neighbors(self, new_node):
        """Encontra nós próximos ao novo nó dentro de um raio definido."""
        return [node for node in self.nodes if self.distance(node, new_node) < self.radius]

    def rewire(self, new_node, neighbors):
        """Reestrutura a árvore para melhorar o caminho."""
        for neighbor in neighbors:
            if self.distance(self.start, new_node) + self.distance(new_node, neighbor) < self.distance(self.start, neighbor):
                neighbor.parent = new_node

    def build_rrt_star(self):
        """Constrói a árvore RRT* e encontra um caminho."""
        for _ in range(self.max_iter):
            # Escolhe aleatoriamente um nó do grafo
            random_node = random.choice(list(self.graph.keys()))
            rand_x, rand_y = self.graph[random_node]
            rand_node = Node(random_node, rand_x, rand_y)
            
            nearest = self.nearest_node(rand_node)
            new_node = self.steer(nearest, rand_node)

            # Adiciona o novo nó à árvore
            new_node.parent = nearest
            self.nodes.append(new_node)
            neighbors = self.find_neighbors(new_node)
            self.rewire(new_node, neighbors)

            # Verifica se o novo nó está suficientemente perto do objetivo
            if self.distance(new_node, self.goal) < self.step_size:
                self.goal.parent = new_node
                self.nodes.append(self.goal)
                return self.get_path()

        return None  # Falha ao encontrar um caminho

    def get_path(self):
        """Reconstrói o caminho do objetivo até o início."""
        path = []
        node = self.goal
        while node:
            path.append((node.x, node.y))
            node = node.parent
        return path[::-1]

    def draw(self, path=None):
        """Desenha o ambiente, os nós e o caminho encontrado."""
        plt.figure(figsize=(8, 8))
        plt.xlim(0, 100)
        plt.ylim(0, 100)

        # Desenha os nós do grafo
        for node_name, (x, y) in self.graph.items():
            plt.plot(x, y, 'bo')  # Nó azul
            plt.text(x, y, node_name, fontsize=12, ha='right')

        # Desenha a árvore RRT*
        for node in self.nodes:
            if node.parent:
                plt.plot([node.x, node.parent.x], [node.y, node.parent.y], "g-", alpha=0.5)

        # Desenha o caminho final
        if path:
            path_x, path_y = zip(*path)
            plt.plot(path_x, path_y, "r-", linewidth=2)

        # Marca início e fim
        plt.plot(self.start.x, self.start.y, "go", markersize=10, label="Início")
        plt.plot(self.goal.x, self.goal.y, "ro", markersize=10, label="Objetivo")

        plt.legend()
        plt.title("RRT* - Planejamento de Caminho")
        plt.show()

# Grafo de exemplo
graph = {
    'A': (10, 10), 'B': (20, 30), 'C': (40, 40), 'D': (60, 20),
    'E': (80, 30), 'F': (30, 60), 'G': (50, 80), 'H': (90, 90)
}

# Configuração do espaço
start = ('A', *graph['A'])  # Nó de partida
goal = ('H', *graph['H'])   # Nó de objetivo

# Executa o RRT*
rrt_star = RRTStar(start, goal, graph)
path = rrt_star.build_rrt_star()

# Desenha o resultado
rrt_star.draw(path)
