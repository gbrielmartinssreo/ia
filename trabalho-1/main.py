import numpy as np

rng = np.random.default_rng()

matriz_inicial = np.arange(9)  
rng.shuffle(matriz_inicial)   
matriz_inicial = matriz_inicial.reshape(3, 3) 

print(matriz_inicial)

