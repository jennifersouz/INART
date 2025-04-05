import pandas as pd
import networkx as nx
import math
import sys
import os
import unidecode

def definir_pesos():
    opcoes = ["distancia", "combustivel", "portagem"]
    prioridades = []
    print("Defina a prioridade dos critérios (Digite os nomes na ordem de importância):")
    while len(prioridades) < 3:
        criterio = input(f"{len(prioridades) + 1}º mais importante ({', '.join(opcoes)}): ").strip().lower()
        criterio_normalizado = unidecode.unidecode(criterio)
    
        match = None
        for opcao in opcoes:
            if criterio_normalizado == unidecode.unidecode(opcao) or opcao.startswith(criterio_normalizado):
                match = opcao
                break
        
        if match and match not in prioridades:
            prioridades.append(match)
        else:
            print("Critério inválido ou repetido, tente novamente.")

    return {prioridades[0]: 2, prioridades[1]: 1, prioridades[2]: 0.5}

def normalizar_nome_cidade(nome):
    nome = nome.strip().title()
    
    try:
        nome = unidecode.unidecode(nome)
    except:
        pass 

    return nome

def csv_para_grafo(nome_arquivo, pesos):
    try:
        df = pd.read_csv(nome_arquivo, header=None, 
                        names=['origem', 'destino', 'distancia', 'combustivel', 'portagem'])
        
        df['origem'] = df['origem'].apply(normalizar_nome_cidade)
        df['destino'] = df['destino'].apply(normalizar_nome_cidade)

        df[['distancia', 'combustivel', 'portagem']] = df[['distancia', 'combustivel', 'portagem']].apply(pd.to_numeric, errors='coerce')

        df.dropna(inplace=True)

        G = nx.DiGraph()
        
        cidades = set(df['origem']).union(set(df['destino']))
        
        pos = nx.spring_layout(nx.Graph([(row['origem'], row['destino']) for _, row in df.iterrows()]))
        coordenadas = {cidade: pos.get(cidade, (0, 0)) for cidade in cidades}
        
        for _, row in df.iterrows():
            custo = (
                row['distancia'] * pesos['distancia'] +
                row['combustivel'] * pesos['combustivel'] +
                row['portagem'] * pesos['portagem']
            )
            G.add_edge(row['origem'], row['destino'], weight=custo)
            
            G.edges[row['origem'], row['destino']]['distancia'] = row['distancia']
            G.edges[row['origem'], row['destino']]['combustivel'] = row['combustivel']
            G.edges[row['origem'], row['destino']]['portagem'] = row['portagem']

        return G, df, coordenadas
    
    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Erro: O arquivo '{nome_arquivo}' está vazio.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao processar o arquivo: {str(e)}")
        sys.exit(1)

def distancia_euclidiana(a, b, coordenadas):
    if not coordenadas or a not in coordenadas or b not in coordenadas:
        return 0 
    
    x_a, y_a = coordenadas[a]
    x_b, y_b = coordenadas[b]
    
    return math.sqrt((x_b - x_a)**2 + (y_b - y_a)**2)

def a_star_melhor_caminho(grafo, origem, destino, coordenadas=None):
    if coordenadas:
        heuristic = lambda a, b: distancia_euclidiana(a, b, coordenadas)
    else:
        heuristic = None 
        
    try:
        caminho = nx.astar_path(grafo, origem, destino, heuristic=heuristic, weight='weight')
        custo_total = nx.path_weight(grafo, caminho, weight='weight')
        
        detalhes = []
        for i in range(len(caminho) - 1):
            origem_i, destino_i = caminho[i], caminho[i+1]
            aresta = grafo.edges[origem_i, destino_i]
            detalhes.append({
                'origem': origem_i,
                'destino': destino_i,
                'distancia': aresta['distancia'],
                'combustivel': aresta['combustivel'],
                'portagem': aresta['portagem'],
                'custo': aresta['weight']
            })
            
        return caminho, custo_total, detalhes
    except nx.NetworkXNoPath:
        return None, None, None

def gerar_matriz_adjacencia(df, grafo):
    nos = sorted(set(df['origem']).union(set(df['destino'])))

    matriz_original = pd.DataFrame(float('inf'), index=nos, columns=nos)
    matriz_ajustada = pd.DataFrame(float('inf'), index=nos, columns=nos)

    for _, row in df.iterrows():
        origem, destino = row['origem'], row['destino']
        custo_original = row['distancia'] + row['combustivel'] + row['portagem']
        matriz_original.loc[origem, destino] = custo_original
        matriz_ajustada.loc[origem, destino] = grafo[origem][destino]['weight']

    matriz_original.replace(float('inf'), None, inplace=True)
    matriz_ajustada.replace(float('inf'), None, inplace=True)

    print("\nMatriz de Adjacência Original:")
    print(matriz_original)

    print("\nMatriz de Adjacência Ajustada (custos):")
    print(matriz_ajustada)

    return matriz_original, matriz_ajustada

def obter_nome_arquivo():
    if len(sys.argv) > 1:
        nome_arquivo = sys.argv[1]

        if os.path.isfile(nome_arquivo):
            return nome_arquivo
        else:
            print(f"Arquivo '{nome_arquivo}' não encontrado. Usando entrada padrão.")
    
    while True:
        nome_arquivo = input("Digite o nome do arquivo CSV (ex.csv): ").strip()
        if os.path.isfile(nome_arquivo):
            return nome_arquivo
        else:
            print(f"Arquivo '{nome_arquivo}' não encontrado. Tente novamente.")

if __name__ == "__main__":
    nome_arquivo = obter_nome_arquivo()
    
    pesos = definir_pesos()
    grafo, df, coordenadas = csv_para_grafo(nome_arquivo, pesos)

    nos_disponiveis = sorted(set(df['origem']).union(set(df['destino'])))
    print("\nNós disponíveis no grafo:", ", ".join(nos_disponiveis))

    while True:
        origem_input = input("\nDigite o nó de origem: ").strip()
        origem = normalizar_nome_cidade(origem_input)
        
        destino_input = input("Digite o nó de destino: ").strip()
        destino = normalizar_nome_cidade(destino_input)

        if origem not in nos_disponiveis:
            matches = [n for n in nos_disponiveis if origem.lower() in n.lower()]
            if matches:
                print(f"Cidade de origem '{origem}' não encontrada. Você quis dizer: {', '.join(matches)}?")
                origem = input("Digite a cidade correta da lista acima: ").strip().title()
        
        if destino not in nos_disponiveis:
            matches = [n for n in nos_disponiveis if destino.lower() in n.lower()]
            if matches:
                print(f"Cidade de destino '{destino}' não encontrada. Você quis dizer: {', '.join(matches)}?")
                destino = input("Digite a cidade correta da lista acima: ").strip().title()

        if origem in nos_disponiveis and destino in nos_disponiveis:
            break
        else:
            print("Origem ou destino inválidos. Tente novamente.")

    caminho, custo_total, detalhes = a_star_melhor_caminho(grafo, origem, destino, coordenadas)

    if caminho:
        caminho_formatado = " → ".join(caminho)
        print(f"\nMelhor caminho encontrado: {caminho_formatado}")
        print(f"Custo total: {custo_total:.2f}")
       
        print("\nDetalhes do percurso:")
        print("-" * 80)
        print(f"{'De':<15} {'Para':<15} {'Distância':>10} {'Combustível':>12} {'Portagem':>8} {'Custo':>8}")
        print("-" * 80)
        for d in detalhes:
            print(f"{d['origem']:<15} {d['destino']:<15} {d['distancia']:>10.2f} {d['combustivel']:>12.2f} {d['portagem']:>8.2f} {d['custo']:>8.2f}")
        print("-" * 80)
    else:
        print("\nNão existe um caminho possível entre os nós selecionados.")

    gerar_matriz_adjacencia(df, grafo)