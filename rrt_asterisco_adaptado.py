import csv
import numpy as np
import matplotlib.pyplot as plt
import random
from collections import defaultdict
import networkx as nx

class Node:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.parent = None

class RRTStar:
    def __init__(self, start_node, goal_node, graph, node_positions, step_size=10, max_iter=500, radius=15):
        self.start = Node(start_node, *node_positions[start_node])
        self.goal = Node(goal_node, *node_positions[goal_node])
        self.graph = graph  # Grafo topológico
        self.node_positions = node_positions  # Coordenadas de cada nó
        self.step_size = step_size
        self.max_iter = max_iter
        self.radius = radius
        self.nodes = [self.start]

    def distance(self, node1, node2):
        return np.hypot(node1.x - node2.x, node1.y - node2.y)

    def nearest_node(self, random_node):
        return min(self.nodes, key=lambda node: self.distance(node, random_node))

    def steer(self, from_node, to_node):
        theta = np.arctan2(to_node.y - from_node.y, to_node.x - from_node.x)
        new_x = from_node.x + self.step_size * np.cos(theta)
        new_y = from_node.y + self.step_size * np.sin(theta)
        return Node(from_node.name, new_x, new_y)

    def find_neighbors(self, new_node):
        return [node for node in self.nodes if self.distance(node, new_node) < self.radius]

    def rewire(self, new_node, neighbors):
        for neighbor in neighbors:
            if self.distance(self.start, new_node) + self.distance(new_node, neighbor) < self.distance(self.start, neighbor):
                neighbor.parent = new_node

    def build_rrt_star(self):
        for _ in range(self.max_iter):
            # Escolher um nó aleatório do grafo
            random_node_name = random.choice(list(self.node_positions.keys()))
            rand_x, rand_y = self.node_positions[random_node_name]
            rand_node = Node(random_node_name, rand_x, rand_y)
            
            nearest = self.nearest_node(rand_node)
            new_node = self.steer(nearest, rand_node)

            # Verificar se o novo nó está próximo de um nó existente no grafo
            closest_graph_node = min(self.node_positions.keys(), 
                                  key=lambda n: np.hypot(new_node.x - self.node_positions[n][0], 
                                                         new_node.y - self.node_positions[n][1]))
            
            # Se estiver próximo o suficiente, atualizar para esse nó do grafo
            close_dist = np.hypot(new_node.x - self.node_positions[closest_graph_node][0], 
                                new_node.y - self.node_positions[closest_graph_node][1])
            if close_dist < self.step_size / 2:
                new_node = Node(closest_graph_node, *self.node_positions[closest_graph_node])

            new_node.parent = nearest
            self.nodes.append(new_node)
            neighbors = self.find_neighbors(new_node)
            self.rewire(new_node, neighbors)

            if self.distance(new_node, self.goal) < self.step_size:
                self.goal.parent = new_node
                self.nodes.append(self.goal)
                return self.get_path()

        return None  

    def get_path(self):
        path = []
        node = self.goal
        while node:
            path.append((node.name, node.x, node.y))
            node = node.parent
        return path[::-1]

    def calculate_path_cost(self, path):
        """Calcula o custo total do caminho baseado no grafo original"""
        total_cost = 0
        for i in range(len(path) - 1):
            node_from = path[i][0]
            node_to = path[i + 1][0]
            
            # Procurar o custo entre esses nós no grafo original
            cost = None
            for neighbor, edge_data in self.graph[node_from]:
                if neighbor == node_to:
                    cost = edge_data[0]  # Pegamos o primeiro valor como custo principal
                    break
            
            if cost is not None:
                total_cost += cost
            else:
                # Se não houver uma aresta direta, usar uma estimativa baseada na distância
                total_cost += self.distance(Node(node_from, *self.node_positions[node_from]), 
                                          Node(node_to, *self.node_positions[node_to]))
                
        return total_cost

    def draw(self, path=None):
        plt.figure(figsize=(10, 10))
        
        # Desenhar arestas do grafo original
        for node_from, connections in self.graph.items():
            for node_to, edge_data in connections:
                plt.plot([self.node_positions[node_from][0], self.node_positions[node_to][0]], 
                         [self.node_positions[node_from][1], self.node_positions[node_to][1]], 
                         'k-', alpha=0.3)
        
        # Desenhar nós do grafo original
        for node_name, (x, y) in self.node_positions.items():
            plt.plot(x, y, 'bo')
            plt.text(x, y, node_name, fontsize=12, ha='right')
        
        # Desenhar arestas da árvore RRT*
        for node in self.nodes:
            if node.parent:
                plt.plot([node.x, node.parent.x], [node.y, node.parent.y], "g-", alpha=0.5)
        
        # Desenhar o caminho encontrado
        if path:
            path_x = [p[1] for p in path]
            path_y = [p[2] for p in path]
            path_names = [p[0] for p in path]
            
            plt.plot(path_x, path_y, "r-", linewidth=2)
            
            # Mostrar a sequência de nós no caminho
            path_label = " → ".join(path_names)
            plt.figtext(0.5, 0.01, f"Caminho: {path_label}", ha="center", fontsize=12)
        
        plt.plot(self.start.x, self.start.y, "go", markersize=10, label="Início")
        plt.plot(self.goal.x, self.goal.y, "ro", markersize=10, label="Objetivo")
        
        plt.legend()
        plt.title("RRT* - Planejamento de Caminho em Grafo Topológico")
        plt.grid(True)
        plt.show()

def detectar_formato_csv(filename):
    """Detecta o formato do arquivo CSV analisando algumas linhas"""
    try:
        # Try utf-8 first, if that fails, try latin-1 which accepts all byte values
        encodings = ['utf-8', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(filename, newline='', encoding=encoding) as csvfile:
                    # Ler algumas linhas para análise
                    reader = csv.reader(csvfile)
                    primeiras_linhas = []
                    for i, row in enumerate(reader):
                        primeiras_linhas.append(row)
                        if i >= 5:  # Analisar até 5 linhas
                            break
                    
                    if not primeiras_linhas:
                        continue
                        
                    # Contar número de colunas nas primeiras linhas
                    num_colunas = [len(row) for row in primeiras_linhas]
                    if not num_colunas:
                        continue
                        
                    # Usar a moda (valor mais frequente) para determinar o número típico de colunas
                    colunas_comuns = max(set(num_colunas), key=num_colunas.count)
                    
                    # Decidir o formato baseado no número de colunas
                    if colunas_comuns == 3:
                        return "simples", 3, encoding  # Formato: origem,destino,custo
                    elif colunas_comuns == 5:
                        return "completo", 5, encoding  # Formato: origem,destino,custo,x,y
                    elif colunas_comuns > 3:
                        return "estendido", colunas_comuns, encoding  # Formato com colunas extras
                    else:
                        continue
            except UnicodeDecodeError:
                # Try the next encoding
                continue
                
        return "desconhecido", 0, "utf-8"
                
    except Exception as e:
        print(f"Erro ao detectar formato: {e}")
        return "desconhecido", 0, "utf-8"

def carregar_grafo_csv(filename):
    """Carrega o grafo de um arquivo CSV detectando automaticamente o formato"""
    formato, num_colunas, encoding = detectar_formato_csv(filename)
    print(f"Formato detectado: {formato} ({num_colunas} colunas), encoding: {encoding}")
    
    grafo = defaultdict(list)
    coordenadas_explicitas = {}
    
    with open(filename, newline='', encoding=encoding) as csvfile:
        reader = csv.reader(csvfile)
        
        for row in reader:
            row = [item.strip() for item in row]  # Remover espaços extras
            
            if len(row) < 3:
                continue  # Ignorar linhas que não têm pelo menos origem, destino e custo
                
            node_a = row[0]
            node_b = row[1]
            
            try:
                # Sempre tentar converter o terceiro valor para número (custo)
                custo = float(row[2])
                
                # Criar uma lista de dados de aresta, começando com o custo
                edge_data = [custo]
                
                # Se temos coordenadas explícitas no CSV (formato completo)
                if len(row) >= 5 and formato in ["completo", "estendido"]:
                    try:
                        x_a, y_a = float(row[3]), float(row[4])
                        coordenadas_explicitas[node_a] = (x_a, y_a)
                        
                        # Se tiver mais valores, adicionar como dados extras da aresta
                        for i in range(5, len(row)):
                            if row[i]:
                                edge_data.append(float(row[i]))
                    except ValueError:
                        # Se não conseguir converter para float, ignorar esses valores
                        pass
                
                # Adicionar a aresta ao grafo
                grafo[node_a].append((node_b, edge_data))
                
            except ValueError:
                print(f"Aviso: Não foi possível converter o custo para número na linha: {row}")
                continue
    
    return grafo, coordenadas_explicitas, formato

def gerar_posicoes_nos(grafo, coordenadas_explicitas=None):
    """Gera posições para os nós do grafo, usando coordenadas explícitas se disponíveis"""
    # Criar um grafo NetworkX
    G = nx.DiGraph()
    
    # Adicionar arestas ao grafo
    for node_from, connections in grafo.items():
        for node_to, edge_data in connections:
            G.add_edge(node_from, node_to, weight=edge_data[0])  # Usar o primeiro valor como peso
    
    # Se temos coordenadas explícitas, usá-las
    if coordenadas_explicitas and len(coordenadas_explicitas) > 0:
        # Verificar se temos coordenadas para todos os nós
        todos_nos = set(grafo.keys()).union({dest for source in grafo for dest, _ in grafo[source]})
        nos_sem_coord = todos_nos - set(coordenadas_explicitas.keys())
        
        if nos_sem_coord:
            print(f"Aviso: {len(nos_sem_coord)} nós não têm coordenadas explícitas. Eles serão posicionados automaticamente.")
            
            # Gerar posições apenas para os nós que faltam
            posicoes_restantes = nx.spring_layout(G.subgraph(nos_sem_coord), seed=42, scale=100)
            
            # Combinar com as coordenadas explícitas
            posicoes_dict = {**coordenadas_explicitas}
            for node, pos in posicoes_restantes.items():
                posicoes_dict[node] = (pos[0], pos[1])
                
            return posicoes_dict
        else:
            # Temos coordenadas para todos os nós
            return coordenadas_explicitas
    else:
        # Gerar posições usando o algoritmo spring_layout
        posicoes = nx.spring_layout(G, seed=42, scale=100)
        return {node: (pos[0], pos[1]) for node, pos in posicoes.items()}

# Programa principal
try:
    # Solicitar o nome do arquivo CSV
    arquivo_csv = input("Digite o nome do arquivo CSV do grafo: ")
    
    # Carregar o grafo do arquivo CSV
    grafo, coordenadas_explicitas, formato = carregar_grafo_csv(arquivo_csv)
    
    if not grafo:
        print("Erro: Não foi possível carregar o grafo. Verifique o arquivo CSV.")
        exit(1)
        
    # Gerar posições para os nós
    posicoes_nos = gerar_posicoes_nos(grafo, coordenadas_explicitas)
    
    # Mostrar nós disponíveis
    nos_disponiveis = sorted(list(set(grafo.keys())))
    print(f"Nós disponíveis no grafo ({len(nos_disponiveis)}): {', '.join(nos_disponiveis)}")
    
    # Solicitar nós de origem e destino
    while True:
        start_node = input("Digite o nó de origem: ").strip()
        if start_node in nos_disponiveis:
            break
        else:
            print(f"Erro: '{start_node}' não é um nó válido. Por favor, escolha um dos nós disponíveis.")
    
    while True:
        goal_node = input("Digite o nó de destino: ").strip()
        if goal_node in nos_disponiveis:
            if goal_node != start_node:
                break
            else:
                print("Erro: O nó de destino não pode ser igual ao nó de origem.")
        else:
            print(f"Erro: '{goal_node}' não é um nó válido. Por favor, escolha um dos nós disponíveis.")
    
    # Criar o planejador RRT*
    rrt_star = RRTStar(start_node, goal_node, grafo, posicoes_nos)
    
    # Executar o algoritmo
    print("Executando algoritmo RRT*...")
    path = rrt_star.build_rrt_star()
    
    # Visualizar o resultado
    if path:
        path_names = [node[0] for node in path]
        path_str = " → ".join(path_names)
        path_cost = rrt_star.calculate_path_cost(path)
        
        print(f"Melhor caminho encontrado: {path_str}")
        print(f"Custo total: {path_cost:.2f}")
    else:
        print("Caminho não encontrado")
    
    # Desenhar o resultado
    rrt_star.draw(path)

except Exception as e:
    import traceback
    print(f"Erro ao executar o programa: {e}")
    print(traceback.format_exc())