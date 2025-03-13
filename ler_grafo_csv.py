import csv

def ler_grafo_csv(nome_ficheiro):
    """
    Lê um grafo de um ficheiro CSV com múltiplos custos.

    Args:
        nome_ficheiro (str): Nome do ficheiro CSV.

    Returns:
        dict: Um dicionário representando o grafo, com nós de origem e suas arestas.
    """
    grafo = {}
    try:
        with open(nome_ficheiro, 'r') as arquivo:
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
    except FileNotFoundError:
        print(f"Erro: O ficheiro '{nome_ficheiro}' não foi encontrado.")
    except ValueError:
        print(f"Erro: Problema ao converter os dados do ficheiro '{nome_ficheiro}'.")
    
    return grafo

# Exemplo de uso com o grafo
grafo = ler_grafo_csv('grafo.csv')  # Nome do ficheiro como argumento
if grafo:
    for origem, destinos in grafo.items():
        print(f"{origem}:")
        for destino, distancia, combustivel, tempo in destinos:
            print(f"  → {destino} | {distancia} km | {combustivel} L | {tempo} min")
