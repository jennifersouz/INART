import csv

def csv_para_matriz_adjacencia(nome_arquivo):
    """
    Lê um grafo a partir de um CSV e converte para uma matriz de adjacência.
    Args:
        nome_arquivo (str): Nome do ficheiro CSV.
    Returns:
        tuple: Uma tupla contendo a lista de nós e a matriz de adjacência.
    """
    # Lê o CSV e armazena os nós e arestas
    grafo = {}
    nos = set()  # Conjunto para armazenar todos os nós únicos

    with open(nome_arquivo, 'r') as arquivo:
        leitor = csv.reader(arquivo)
        for linha in leitor:
            origem, destino, distancia, combustivel, tempo = linha
            distancia = int(distancia)
            combustivel = int(combustivel)
            tempo = int(tempo)

            # Adiciona os nós ao conjunto
            nos.add(origem)
            nos.add(destino)

            # Adiciona a aresta ao grafo
            if origem not in grafo:
                grafo[origem] = []
            grafo[origem].append((destino, distancia, combustivel, tempo))

    # Converte o conjunto de nós para uma lista ordenada
    nos = sorted(nos)

    # Inicializa a matriz de adjacência com float('inf') para indicar a ausência de aresta
    matriz_adjacencia = [[float('inf') for _ in range(len(nos))] for _ in range(len(nos))]

    # Preenche a matriz de adjacência com os custos das arestas (somando distância, combustível e tempo)
    for origem in grafo:
        for destino, distancia, combustivel, tempo in grafo[origem]:
            i = nos.index(origem)  # Índice do nó de origem
            j = nos.index(destino)  # Índice do nó de destino
            matriz_adjacencia[i][j] = distancia + combustivel + tempo  # Soma os três custos

    return nos, matriz_adjacencia

# Exemplo de uso
if __name__ == "__main__":
    # Nome do arquivo CSV
    nome_arquivo = 'grafo.csv'

    # Ler o grafo do CSV e gerar a matriz de adjacência
    nos, matriz_adjacencia = csv_para_matriz_adjacencia(nome_arquivo)

    # Exibe a lista de nós
    print("Nós:", nos)

    # Exibe a matriz de adjacência
    print("Matriz de adjacência:")
    for linha in matriz_adjacencia:
        print(linha)
