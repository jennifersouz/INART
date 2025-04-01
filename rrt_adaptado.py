import pandas as pd
from queue import PriorityQueue
import networkx as nx
import matplotlib.pyplot as plt
import random
from mpl_toolkits.mplot3d import Axes3D


def carregar_grafo_de_csv(nome_arquivo, criterio):
    "Lê um grafo a partir de um CSV e converte para estrutura utilizável."
    df = pd.read_csv(nome_arquivo, header=None)
    df.columns = ['Origem', 'Destino', 'Portagem', 'Combustivel', 'Distancia']
    criterios = {'portagem': 'Portagem', 'combustivel': 'Combustivel', 'distancia': 'Distancia'}

    if criterio not in criterios:
        raise ValueError("Critério inválido! Escolha entre: distancia, combustivel, portagem")

    grafo = {}
    for _, row in df.iterrows():
        origem, destino, custo = row['Origem'], row['Destino'], row[criterios[criterio]]
        if origem not in grafo:
            grafo[origem] = []
        grafo[origem].append((destino, custo))
    return grafo


def a_star(grafo, start, end):
    "Executa o algoritmo A* para encontrar o menor caminho."
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {start: 0}

    while not open_set.empty():
        _, current = open_set.get()
        if current == end:
            return reconstruct_path(came_from, end), g_score[current]

        for neighbor, cost in grafo.get(current, []):
            temp_g_score = g_score[current] + cost
            if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                open_set.put((temp_g_score, neighbor))

    return [], float('inf')


def reconstruct_path(came_from, end):
    "Reconstrói o caminho encontrado."
    path = []
    current = end
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.append(current)
    path.reverse()
    return path


def calcular_rtt(grafo, start, end):
    """Calcula o RTT como ida + volta."""
    path_ida, custo_ida = a_star(grafo, start, end)
    path_volta, custo_volta = a_star(grafo, end, start)

    if not path_ida or not path_volta:
        return [], float('inf')

    # Combina os caminhos, evitando duplicar o nó intermediário
    path_completo = path_ida + path_volta[1:]
    custo_total = custo_ida + custo_volta
    return path_completo, custo_total


def desenhar_grafo_3d(grafo, path=None):

    G = nx.DiGraph()

    # Adiciona as arestas ao objeto Graph
    for origem in grafo:
        for destino, custo in grafo[origem]:
            G.add_edge(origem, destino, weight=custo)

    # Layout 2D
    pos_2d = nx.spring_layout(G, k=2, iterations=100, seed=42)
    # k maior e mais iterações ajudam a "espalhar" mais o grafo,

    # Converte layout 2D para 3D adicionando uma coordenada Z aleatória
    random.seed(42)
    pos_3d = {}
    for node, (x, y) in pos_2d.items():
        z = random.uniform(-3, 3)
        pos_3d[node] = (x, y, z)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Desenha nós
    for node in G.nodes():
        x, y, z = pos_3d[node]
        ax.scatter(x, y, z, c='b', s=50)
        ax.text(x, y, z, ' ' + node, fontsize=8, color='black')

    # Desenha arestas
    for (u, v) in G.edges():
        x_vals = [pos_3d[u][0], pos_3d[v][0]]
        y_vals = [pos_3d[u][1], pos_3d[v][1]]
        z_vals = [pos_3d[u][2], pos_3d[v][2]]

        if path and any(u == path[i] and v == path[i + 1] for i in range(len(path) - 1)):
            # Aresta no caminho cor vermelha, alpha=1, linha mais grossa
            ax.plot(x_vals, y_vals, z_vals, color='red', linewidth=2.5, alpha=1.0)
        else:
            # Aresta fora do caminho cor preta, alpha baixo, linha mais fina
            ax.plot(x_vals, y_vals, z_vals, color='black', linewidth=0.8, alpha=0.1)

    ax.set_title("RTT - Grafo em 3D")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.tight_layout()
    plt.show()


def main():
    nome_arquivo = 'grafo_grande.csv'
    criterio = input("Escolha o critério de custo (distancia/combustivel/portagem): ").strip().lower()

    try:
        grafo = carregar_grafo_de_csv(nome_arquivo, criterio)
    except ValueError as e:
        print(e)
        return

    start = input("Digite o nó de origem: ").strip()
    end = input("Digite o nó de destino: ").strip()

    path, cost = calcular_rtt(grafo, start, end)

    print("\nCaminho encontrado:", " -> ".join(path))
    print("Custo total:", cost)

    desenhar_grafo_3d(grafo, path)


if __name__ == "__main__":
    main()