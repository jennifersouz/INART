import pandas as pd

def csv_para_matriz_adjacencia(nome_arquivo, top_n=10):
    """
    Lê um grafo a partir de um CSV e converte para uma matriz de adjacência,
    considerando o custo como a soma de distância, combustível e tempo.

    Args:
        nome_arquivo (str): Nome do arquivo CSV.
        top_n (int): Número de menores custos a exibir.

    Returns:
        pd.DataFrame: Matriz de adjacência contendo os menores custos.
    """
    # Lê o CSV
    df = pd.read_csv(nome_arquivo, header=None, names=['origem', 'destino', 'distancia', 'combustivel', 'tempo'])

    # Converte colunas numéricas
    df[['distancia', 'combustivel', 'tempo']] = df[['distancia', 'combustivel', 'tempo']].apply(pd.to_numeric, errors='coerce')

    # Remove linhas inválidas
    df.dropna(inplace=True)

    # Calcula custo total como a soma de distância, combustível e tempo
    df['custo'] = df['distancia'] + df['combustivel'] + df['tempo']

    # Lista de nós únicos
    nos = sorted(set(df['origem']).union(set(df['destino'])))

    # Cria matriz de adjacência vazia
    matriz_adjacencia = pd.DataFrame(float('inf'), index=nos, columns=nos)

    # Preenche a matriz com os menores custos encontrados
    for _, row in df.iterrows():
        origem, destino, custo = row['origem'], row['destino'], row['custo']
        matriz_adjacencia.loc[origem, destino] = min(matriz_adjacencia.loc[origem, destino], custo)

    # Substitui 'inf' por None para melhor legibilidade
    matriz_adjacencia.replace(float('inf'), None, inplace=True)

    # Encontra os menores custos
    menores_custos = df.nsmallest(top_n, 'custo')

    print("\nMenores custos encontrados:")
    print(menores_custos[['origem', 'destino', 'custo']])

    return matriz_adjacencia

# Exemplo de uso
if __name__ == "__main__":
    nome_arquivo = 'grafo.csv'
    matriz_adjacencia = csv_para_matriz_adjacencia(nome_arquivo)

    print("\nMatriz de Adjacência (Apenas menores custos):")
    print(matriz_adjacencia)
