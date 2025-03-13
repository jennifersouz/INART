from queue import PriorityQueue

def a_star(graph, start, end):
    """
    Executa o algoritmo A* para encontrar o caminho mais curto de 'start' até 'end' num grafo.
    Args:
        graph (dict): O grafo representado como um dicionário de listas de adjacência.
        start (str): O nó de início.
        end (str): O nó de destino.
    Returns:
        tuple: Uma tupla contendo o caminho (lista de nós) e o custo total (int).
    """
    # Fila de prioridade para os nós a serem explorados
    open_set = PriorityQueue()
    open_set.put((0, start))  # (f_score, nó atual)
    came_from = {}  # Dicionário para reconstruir o caminho percorrido

    # g_score: custo do caminho mais curto conhecido de 'start' até cada nó
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0

    # f_score: estimativa do custo total de 'start' até 'end' passando pelo nó atual
    f_score = {node: float('inf') for node in graph}
    f_score[start] = heuristic(start, end)

    # Conjunto auxiliar para rastrear os nós na fila de prioridade
    open_set_hash = {start}

    while not open_set.empty():
        # Obter o nó com o menor f_score da fila
        _, current = open_set.get()
        open_set_hash.remove(current)

        # Se chegamos ao destino, reconstruímos e retornamos o caminho
        if current == end:
            path = reconstruct_path(came_from, end)
            return path, g_score[end]

        # Explorar os vizinhos do nó atual
        for neighbor, cost in graph[current]:
            # Calcula o custo temporário para alcançar o vizinho
            temp_g_score = g_score[current] + cost

            # Se encontramos um caminho melhor para o vizinho, atualizamos os valores
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor, end)

                # Se o vizinho ainda não está na fila, adicionamos
                if neighbor not in open_set_hash:
                    open_set.put((f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)

    # Se não for possível encontrar um caminho, retorna um caminho vazio e custo infinito
    return [], float('inf')

def heuristic(node, end):
    """
    Função heurística simples. Neste caso, retorna 0 para que o A* funcione como Dijkstra.
    Args:
        node (str): O nó atual.
        end (str): O nó de destino.
    Returns:
        int: O valor heurístico (neste caso, sempre 0).
    """
    return 0  # Pode ser substituído por uma heurística real

def reconstruct_path(came_from, end):
    """
    Reconstrói o caminho desde o nó inicial até o destino.
    Args:
        came_from (dict): Dicionário que contém a relação entre nós para reconstrução do caminho.
        end (str): O nó de destino.
    Returns:
        list: Lista representando o caminho do início ao destino.
    """
    path = []
    current = end
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.append(current)  # Adiciona o nó inicial
    path.reverse()  # Inverte a lista para ficar na ordem correta
    return path

# Uso grafo (8)
if __name__ == "__main__":
    # Definição do grafo como um dicionário de listas de adjacência
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

    # Definir nó inicial e nó objetivo
    start = 'A'
    end = 'H'

    # Executar o algoritmo A*
    path, cost = a_star(graph, start, end)

    # Exibir os resultados
    print("Caminho encontrado:", path)
    print("Custo total:", cost)
