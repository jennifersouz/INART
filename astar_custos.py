from queue import PriorityQueue
import csv

def a_star(graph, start, end):
    """
    Perform an A* search from start to end on the given graph.

    Args:
        graph (dict): The graph represented as a dictionary of adjacency lists.
        start (str): The starting node.
        end (str): The target node.

    Returns:
        tuple: A tuple containing the path (list) and the total cost (int).
    """
    # Priority queue for open set
    open_set = PriorityQueue()
    open_set.put((0, start))  # (f_score, node)
    came_from = {}  # To reconstruct the path

    # g_score: cost from start to current node
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0

    # f_score: estimated total cost from start to end through current node
    f_score = {node: float('inf') for node in graph}
    f_score[start] = heuristic(start, end)

    open_set_hash = {start}  # To keep track of nodes in the open set

    while not open_set.empty():
        # Get the node with the lowest f_score
        _, current = open_set.get()
        open_set_hash.remove(current)

        # If we reached the end, reconstruct and return the path
        if current == end:
            path = reconstruct_path(came_from, end)
            return path, g_score[end]

        # Explore neighbors
        for neighbor, distancia, combustivel, tempo in graph.get(current, []):
            # Calcular o custo total (soma dos três custos)
            custo_total = distancia + combustivel + tempo

            # Calculate tentative g_score
            temp_g_score = g_score[current] + custo_total

            # If this path to neighbor is better, update the data
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor, end)

                # Add neighbor to open set if not already there
                if neighbor not in open_set_hash:
                    open_set.put((f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)

    # If the loop ends, no path was found
    return [], float('inf')

def heuristic(node, end):
    """
    Simple heuristic function (can be improved if needed).
    For now, it returns 0 to make A* behave like Dijkstra's algorithm.
    """
    return 0

def reconstruct_path(came_from, end):
    """
    Reconstruct the path from start to end using the came_from dictionary.

    Args:
        came_from (dict): Dictionary containing the path information.
        end (str): The target node.

    Returns:
        list: The path from start to end.
    """
    path = []
    current = end
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.append(current)  # Add the start node
    path.reverse()  # Reverse to get the path from start to end
    return path

def ler_grafo_csv(nome_arquivo):
    """
    Lê um grafo a partir de um ficheiro CSV com múltiplos custos.

    Args:
        nome_arquivo (str): Nome do ficheiro CSV.

    Returns:
        dict: Grafo representado como um dicionário de adjacência.
    """
    grafo = {}
    with open(nome_arquivo, 'r') as arquivo:
        leitor = csv.reader(arquivo)
        for linha in leitor:
            origem, destino, distancia, combustivel, tempo = linha
            distancia = int(distancia)  # Converte para inteiro
            combustivel = int(combustivel)  # Converte para inteiro
            tempo = int(tempo)  # Converte para inteiro

            # Adiciona a aresta ao grafo
            if origem not in grafo:
                grafo[origem] = []
            grafo[origem].append((destino, distancia, combustivel, tempo))
    return grafo

# Exemplo de uso
if __name__ == "__main__":
    # Ler o grafo do CSV
    nome_arquivo = "grafo.csv"  # Substitua pelo nome do seu ficheiro CSV
    grafo = ler_grafo_csv(nome_arquivo)

    # Definir nó inicial e nó objetivo
    start = 'A'
    end = 'H'

    # Executar A*
    path, cost = a_star(grafo, start, end)

    # Resultados
    print("Caminho encontrado:", path)
    print("Custo total:", cost) #custo total(distancia,tempo,combustivel etc)