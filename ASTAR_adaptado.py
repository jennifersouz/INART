#https://stackabuse.com/basic-ai-concepts-a-search-algorithm/
import networkx as nx
import matplotlib.pyplot as plt
from queue import PriorityQueue
import time

start_time =time.time()
def a_star(graph, start, end):
    if start not in graph or end not in graph:
        return [], float('inf')

    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    f_score = {node: float('inf') for node in graph}
    f_score[start] = heuristic(start, end)
    open_set_hash = {start}

    while not open_set.empty():
        _, current = open_set.get()
        open_set_hash.remove(current)

        if current == end:
            path = reconstruct_path(came_from, end)
            return path, g_score[end]

        for neighbor, cost in graph[current]:
            temp_g_score = g_score[current] + cost

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor, end)

                if neighbor not in open_set_hash:
                    open_set.put((f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)

    return [], float('inf')

def heuristic(node, end):
    return 1  

def reconstruct_path(came_from, end):
    """Reconstrói o caminho encontrado."""
    path = []
    current = end
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.append(current)
    path.reverse()
    return path

def desenhar_grafo(graph, path=None):
    """Desenha o grafo e destaca o caminho encontrado."""
    G = nx.Graph()
    for node, neighbors in graph.items():
        for neighbor, weight in neighbors:
            G.add_edge(node, neighbor, weight=weight)

    pos = nx.spring_layout(G)
    plt.figure(figsize=(8, 6))

    nx.draw(G, pos, with_labels=True, node_size=700, node_color="lightblue", font_size=10, edge_color="gray")
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    if path:
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color="red", width=2)
        nx.draw_networkx_nodes(G, pos, nodelist=path, node_size=800, node_color="orange")

    plt.title("Grafo e Caminho Encontrado")
    plt.show()

# Grafo de exemplo
graph = {
    'A': [('B', 5), ('F', 3)],
    'B': [('A', 5), ('C', 2), ('G', 3)],
    'C': [('B', 2), ('D', 6), ('H', 10)],
    'D': [('C', 6), ('E', 3)],
    'E': [('D', 3), ('F', 8), ('H', 5)],
    'F': [('E', 8), ('A', 3), ('G', 7)],
    'G': [('F', 7), ('H', 2), ('B', 3)],
    'H': [('G', 2), ('E', 5), ('C', 10)],
}

# Perguntar ao usuário a origem e destino
start = input("Digite o nó de origem: ").strip()
end = input("Digite o nó de destino: ").strip()

# Verificar se ambos os nós estão no grafo
if start not in graph or end not in graph:
    print("Erro: Um ou ambos nós não existem no grafo.")
else:
    # Executar o algoritmo A*
    path, cost = a_star(graph, start, end)

    if path:
        print("\nCaminho encontrado:", " -> ".join(path))
        print("Custo total:", cost)
    else:
        print("\nNão foi possível encontrar um caminho entre", start, "e", end)

    # Exibir o grafo
    desenhar_grafo(graph, path)

    end_time=time.time()
    execution_time = end_time - start_time
    print(f"Tempo de execução: {execution_time: .4f} segundos")