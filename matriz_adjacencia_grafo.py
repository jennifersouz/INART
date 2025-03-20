import pandas as pd
import networkx as nx

def definir_pesos():
    """
    Pede ao usuário a ordem de prioridade (distância, combustível, tempo) e define os pesos.
    Retorna um dicionário com os pesos correspondentes.
    """
    opcoes = ["distancia", "combustivel", "tempo"]
    prioridades = []
    print("Defina a prioridade dos critérios (Digite os nomes na ordem de importância):")
    while len(prioridades) < 3:
        criterio = input(f"{len(prioridades) + 1}º mais importante ({', '.join(opcoes)}): ").strip().lower()
        if criterio in opcoes and criterio not in prioridades:
            prioridades.append(criterio)
        else:
            print("Critério inválido ou repetido, tente novamente.")

    return {prioridades[0]: 2, prioridades[1]: 1, prioridades[2]: 0.5}

def csv_para_grafo(nome_arquivo, pesos):
    """
    Lê um CSV contendo as arestas de um grafo e converte para um grafo direcionado.

    Args:
        nome_arquivo (str): Nome do arquivo CSV.
        pesos (dict): Pesos atribuídos para distância, combustível e tempo.

    Returns:
        nx.DiGraph: Grafo direcionado com pesos ajustados.
    """
    df = pd.read_csv(nome_arquivo, header=None, names=['origem', 'destino', 'distancia', 'combustivel', 'tempo'])

    # Padronizar nomes das cidades
    df['origem'] = df['origem'].str.strip().str.title()
    df['destino'] = df['destino'].str.strip().str.title()

    # Converter colunas numéricas
    df[['distancia', 'combustivel', 'tempo']] = df[['distancia', 'combustivel', 'tempo']].apply(pd.to_numeric, errors='coerce')

    # Remover linhas inválidas
    df.dropna(inplace=True)

    # Criar o grafo
    G = nx.DiGraph()
    for _, row in df.iterrows():
        custo = (
            row['distancia'] * pesos['distancia'] +
            row['combustivel'] * pesos['combustivel'] +
            row['tempo'] * pesos['tempo']
        )
        G.add_edge(row['origem'], row['destino'], weight=custo)

    return G, df

def a_star_melhor_caminho(grafo, origem, destino):
    """
    Aplica o algoritmo A* para encontrar o melhor caminho entre dois nós.

    Args:
        grafo (nx.DiGraph): Grafo direcionado com pesos.
        origem (str): Nó de origem.
        destino (str): Nó de destino.

    Returns:
        tuple: Melhor caminho (lista de nós) e o custo total.
    """
    try:
        caminho = nx.astar_path(grafo, origem, destino, weight='weight')
        custo_total = nx.path_weight(grafo, caminho, weight='weight')
        return caminho, custo_total
    except nx.NetworkXNoPath:
        return None, None

def gerar_matriz_adjacencia(df, grafo):
    """
    Gera e exibe a matriz de adjacência do grafo original e do grafo ajustado.

    Args:
        df (pd.DataFrame): DataFrame original do CSV.
        grafo (nx.DiGraph): Grafo ajustado com os custos recalculados.

    Returns:
        tuple: Matrizes de adjacência original e ajustada.
    """
    nos = sorted(set(df['origem']).union(set(df['destino'])))

    matriz_original = pd.DataFrame(float('inf'), index=nos, columns=nos)
    matriz_ajustada = pd.DataFrame(float('inf'), index=nos, columns=nos)

    for _, row in df.iterrows():
        origem, destino = row['origem'], row['destino']
        custo_original = row['distancia'] + row['combustivel'] + row['tempo']
        matriz_original.loc[origem, destino] = custo_original
        matriz_ajustada.loc[origem, destino] = grafo[origem][destino]['weight']

    matriz_original.replace(float('inf'), None, inplace=True)
    matriz_ajustada.replace(float('inf'), None, inplace=True)

    print("\nMatriz de Adjacência Original:")
    print(matriz_original)

    print("\nMatriz de Adjacência Ajustada (custos):")
    print(matriz_ajustada)

    return matriz_original, matriz_ajustada

if __name__ == "__main__":
    nome_arquivo = 'cities_nodes_special.csv'

    pesos = definir_pesos()
    grafo, df = csv_para_grafo(nome_arquivo, pesos)

    nos_disponiveis = sorted(set(df['origem']).union(set(df['destino'])))
    print("\nNós disponíveis no grafo:", ", ".join(nos_disponiveis))

    while True:
        origem = input("\nDigite o nó de origem: ").strip().title()
        destino = input("Digite o nó de destino: ").strip().title()

        if origem in nos_disponiveis and destino in nos_disponiveis:
            break
        else:
            print("Origem ou destino inválidos. Tente novamente.")

    caminho, custo_total = a_star_melhor_caminho(grafo, origem, destino)

    if caminho:
        caminho_formatado = " → ".join(caminho)
        print(f"\nMelhor caminho encontrado: {caminho_formatado}")
        print(f"Custo total: {custo_total:.2f}")
    else:
        print("\nNão existe um caminho possível entre os nós selecionados.")

    gerar_matriz_adjacencia(df, grafo)
