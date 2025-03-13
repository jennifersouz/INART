import csv 

def ler_grafo_csv(nome_ficheiro): 
    grafo = {}
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
    
    return grafo

#Uso com o grafo
grafo = ler_grafo_csv('grafo.csv')  # Nome do ficheiro como argumento
for origem, destinos in grafo.items():
    print(f"{origem}:")
    for destino, distancia, combustivel, tempo in destinos:
        print(f"  → {destino} | {distancia} km | {combustivel} L | {tempo} min")
