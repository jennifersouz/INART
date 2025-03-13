from queue import PriorityQueue
import csv

def a_star(graph, start, end):
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

        for neighbor, distancia, combustivel, tempo in graph.get(current, []):
            custo_total = distancia + combustivel + tempo  
            temp_g_score = g_score[current] + custo_total

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor, end)

                if neighbor not in open_set_hash:
                    open_set.put((f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)

    return [], float('inf')

def heuristic(node, end):
    estimativas_distancias = {
        'A': 4, 'B': 3, 'C': 2, 'D': 1, 'E': 2, 'F': 3, 'G': 1, 'H': 0
    }
    return estimativas_distancias.get(node, 0)

def reconstruct_path(came_from, end):
    path = []
    current = end
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.append(current)
    path.reverse()
    return path

def ler_grafo_csv(nome_arquivo):
    grafo = {}
    with open(nome_arquivo, 'r') as arquivo:
        leitor = csv.reader(arquivo)
        for linha in leitor:
            origem, destino, distancia, combustivel, tempo = linha
            distancia = int(distancia)
            combustivel = int(combustivel)
            tempo = int(tempo)

            if origem not in grafo:
                grafo[origem] = []
            grafo[origem].append((destino, distancia, combustivel, tempo))
    return grafo

# Exemplo de uso
if __name__ == "__main__":
    nome_arquivo = "grafo.csv"
    grafo = ler_grafo_csv(nome_arquivo)
    start = 'A'
    end = 'H'
    path, cost = a_star(grafo, start, end)

    print("Caminho encontrado:", path)
    print("Custo total:", cost)
