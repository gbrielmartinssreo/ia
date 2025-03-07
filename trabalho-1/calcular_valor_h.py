import numpy as np

def manhattan(matriz_atual,matriz_destino):
    distancia = 0;
    for linha_atual in range(3):
        for coluna_atual in range(3):
            numero = matriz_atual[linha_atual,coluna_atual]
            if numero !=0:
                linha_destino,coluna_destino = np.where(matriz_destino == numero)
                distancia += np.abs(linha_atual-linha_destino[0])+np.abs(coluna_atual-coluna_destino[0])
                return distancia

def hamming(matriz_atual,matriz_destino):
    qtde_fora_lugar = len(matriz_atual[np.where(matriz_atual!=matriz_destino)])
    
    return (qtde_fora_lugar-1 if qtde_fora_lugar>0 else 0)

def calcular_valor_h(matriz_atual, matriz_destino,heuristica):
    if heuristica==1:
        return manhattan(matriz_atual,matriz_destino);

    if heuristica==2:
        return hamming(matriz_atual,matriz_destino);

