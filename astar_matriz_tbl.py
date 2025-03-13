from tabulate import tabulate
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

    # Inicializa a matriz de adjacência com None (ou "Sem conexão")
    matriz_adjacencia = [[None for _ in range(len(nos))] for _ in range(len(nos))]

    # Preenche a matriz de adjacência com os custos das arestas
    for origem in grafo:
        for destino, distancia, combustivel, tempo in grafo[origem]:
            i = nos.index(origem)  # Índice do nó de origem
            j = nos.index(destino)  # Índice do nó de destino
            matriz_adjacencia[i][j] = (distancia, combustivel, tempo)

    return nos, matriz_adjacencia

# Exemplo de uso
nos, matriz_adjacencia = csv_para_matriz_adjacencia('grafo.csv')

# Prepara os dados para a tabela
dados_tabela = []
for i, linha in enumerate(matriz_adjacencia):
    linha_tabela = [nos[i]]  # Adiciona o nó de origem na primeira coluna
    for custo in linha:
        if custo is None:
            linha_tabela.append("Sem conexão")
        else:
            distancia, combustivel, tempo = custo
            linha_tabela.append(f"{distancia} km, {combustivel} L, {tempo} min")
    dados_tabela.append(linha_tabela)

# Exibe a tabela
cabecalho = ["Nó"] + nos  # Cabeçalho da tabela
print(tabulate(dados_tabela, headers=cabecalho, tablefmt="grid"))
