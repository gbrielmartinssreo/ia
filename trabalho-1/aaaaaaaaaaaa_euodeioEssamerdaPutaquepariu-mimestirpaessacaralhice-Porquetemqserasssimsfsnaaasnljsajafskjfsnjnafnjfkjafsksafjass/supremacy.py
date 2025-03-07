import heapq
import numpy as np
import matplotlib.pyplot as plt
from time import time
import copy

class Metricas:
    """
    Classe para armazenar métricas de desempenho do algoritmo de busca.
    Substitui os dicionários para uma abordagem mais orientada a objetos.
    """
    def __init__(self, nodos_expandidos=0, profundidade=-1, tempo=0):
        self.nodos_expandidos = nodos_expandidos
        self.profundidade = profundidade
        self.tempo = tempo
        
    def __str__(self):
        """Retorna uma representação em string das métricas para exibição"""
        if self.profundidade == -1:
            return "Sem solução encontrada"
        
        return (f"Estatísticas:\n"
                f"Nós expandidos: {self.nodos_expandidos}\n"
                f"Profundidade da solução: {self.profundidade}\n"
                f"Tempo de execução: {self.tempo:.4f} segundos")
                
    def atualizar_tempo(self, inicio_tempo):
        """Atualiza o tempo de execução com base no tempo inicial fornecido"""
        self.tempo = time() - inicio_tempo
        
    def to_dict(self):
        """Converte as métricas para um dicionário (para compatibilidade)"""
        return {
            "nodos_expandidos": self.nodos_expandidos,
            "profundidade": self.profundidade,
            "tempo": self.tempo
        }


class Estado:
    """Representa um estado do puzzle com métodos para comparação e análise"""
    def __init__(self, matriz, d, h, pai=None):
        self.matriz = matriz  # representação da matriz do puzzle
        self.d = d            # profundidade (custo até aqui)
        self.h = h            # heurística
        self.c = d + h        # custo total
        self.pai = pai        # estado pai (objeto Estado ou None)

    def __lt__(self, outro):
        """Para ordenação na fila de prioridade"""
        return self.c < outro.c
        
    def eh_igual(self, outro_estado):
        """Verifica se dois estados são iguais comparando suas matrizes"""
        return np.array_equal(self.matriz, outro_estado.matriz)
        
    def get_matriz_tupla(self):
        """Converte a matriz numpy para tupla de tuplas (para uso como chave em dicionários)"""
        return tuple(map(tuple, self.matriz))


class SlidingPuzzle:
    """Classe principal para resolver o jogo Sliding Puzzle usando A*"""
    def __init__(self):
        # Estado objetivo padrão
        self.matriz_destino = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        
    def manhattan(self, matriz_atual, matriz_destino, peso=1):
        """Calcula a distância de Manhattan entre a matriz atual e o objetivo"""
        distancia = 0
        for linha_atual in range(3):
            for coluna_atual in range(3):
                numero = matriz_atual[linha_atual, coluna_atual]
                if numero != 0:
                    linha_destino, coluna_destino = np.where(matriz_destino == numero)
                    distancia += (abs(linha_atual - linha_destino[0]) + 
                                 abs(coluna_atual - coluna_destino[0])) * peso
        return distancia 

    def hamming(self, matriz_atual, matriz_destino):
        """Calcula a distância de Hamming (número de peças fora do lugar)"""
        return np.sum(matriz_atual != matriz_destino) - 1 if np.sum(matriz_atual != matriz_destino) > 0 else 0

    def manhattan_ponderada(self, matriz_atual, matriz_destino):
        """Manhattan com peso adicional para valorizar mais certas posições"""
        peso = 1.5
        return self.manhattan(matriz_atual, matriz_destino, peso)

    def heuristicas_combinadas(self, matriz_atual, matriz_destino):
        """Combina heurísticas tomando o máximo valor entre elas"""
        return max(
            self.manhattan(matriz_atual, matriz_destino),
            self.hamming(matriz_atual, matriz_destino) * 2,
        )

    def calcular_valor_h(self, matriz_atual, matriz_destino, heuristica):
        """Calcula o valor da heurística baseado na função selecionada"""
        if heuristica == 1:
            return self.manhattan(matriz_atual, matriz_destino)
        elif heuristica == 2:
            return self.hamming(matriz_atual, matriz_destino)
        elif heuristica == 3:
            return self.manhattan_ponderada(matriz_atual, matriz_destino)
        elif heuristica == 4:
            return self.heuristicas_combinadas(matriz_atual, matriz_destino)
        return 0
        
    def get_vizinhos(self, matriz):
        """Gera todos os estados vizinhos possíveis"""
        vizinhos = []
        linha_zero, coluna_zero = np.where(matriz == 0)
        linha_zero, coluna_zero = linha_zero[0], coluna_zero[0]

        movimentos = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # cima, baixo, esquerda, direita

        for move_linha, move_coluna in movimentos:
            nova_linha, nova_coluna = linha_zero + move_linha, coluna_zero + move_coluna

            if 0 <= nova_linha < 3 and 0 <= nova_coluna < 3:
                nova_matriz = matriz.copy()
                nova_matriz[linha_zero, coluna_zero], nova_matriz[nova_linha, nova_coluna] = (
                    nova_matriz[nova_linha, nova_coluna],
                    nova_matriz[linha_zero, coluna_zero],
                )
                vizinhos.append(nova_matriz)

        return vizinhos
    
    def e_solucionavel(self, matriz):
        """Verifica se a configuração do puzzle tem solução"""
        array = [num for row in matriz for num in row if num != 0]
        
        inversoes = 0
        for i in range(len(array)):
            for j in range(i + 1, len(array)):
                if array[i] > array[j]:
                    inversoes += 1
        
        return inversoes % 2 == 0
    
    def array_pra_tupla(self, array):
        """Converte um array NumPy para uma tupla de tuplas"""
        return tuple(map(tuple, array))
    
    def reconstruir_caminho(self, estado_final, estados):
        """Reconstrói o caminho da solução a partir do estado final"""
        caminho = []
        estado_atual = estado_final
        while estado_atual:
            caminho.append(np.array(estado_atual.matriz))
            estado_atual = estados.get(estado_atual.pai)
        caminho.reverse()
        return caminho
        
    def busca_a_estrela(self, matriz_inicial, matriz_destino, heuristica):
        """
        Implementa o algoritmo A* para buscar uma solução.
        Retorna uma tupla (solução, métricas)
        """
        # Verificar se é solucionável
        if not self.e_solucionavel(matriz_inicial) == self.e_solucionavel(matriz_destino):
            return None, Metricas()  # Retorna objeto Metricas vazio
        
        # Inicializar métricas
        metricas = Metricas()
        inicio_tempo = time()
        
        lista_aberta = []
        lista_fechada = set()  # Estados já expandidos
        estados_abertos = {}   # Estados na lista aberta
        estados = {}          # Mapeamento matriz -> estado
        
        # Criar estado inicial
        estado_inicial = Estado(
            self.array_pra_tupla(matriz_inicial), 
            0, 
            self.calcular_valor_h(matriz_inicial, matriz_destino, heuristica)
        )
        
        heapq.heappush(lista_aberta, (estado_inicial.c, id(estado_inicial), estado_inicial))
        estados_abertos[estado_inicial.get_matriz_tupla()] = estado_inicial
        
        while lista_aberta:
            _, _, estado_atual = heapq.heappop(lista_aberta)
            estados_abertos.pop(estado_atual.get_matriz_tupla(), None)
            
            # Se já verificamos este estado, pule
            if estado_atual.get_matriz_tupla() in lista_fechada:
                continue
                
            # Marcar como expandido
            lista_fechada.add(estado_atual.get_matriz_tupla())
            estados[estado_atual.get_matriz_tupla()] = estado_atual
            metricas.nodos_expandidos += 1  # Incrementar contador de nós
            
            # Se encontramos a solução
            if estado_atual.get_matriz_tupla() == self.array_pra_tupla(matriz_destino):
                metricas.profundidade = estado_atual.d
                metricas.atualizar_tempo(inicio_tempo)
                return self.reconstruir_caminho(estado_atual, estados), metricas
                
            # Expandir vizinhos
            for vizinho in self.get_vizinhos(np.array(estado_atual.matriz)):
                matriz_vizinho = self.array_pra_tupla(vizinho)
                
                # Pular estados já expandidos
                if matriz_vizinho in lista_fechada:
                    continue
                    
                # Calcular g para o novo caminho
                novo_g = estado_atual.d + 1
                
                # Se já está na lista aberta, verificar se este caminho é melhor
                if matriz_vizinho in estados_abertos:
                    estado_existente = estados_abertos[matriz_vizinho]
                    if novo_g >= estado_existente.d:
                        continue  # Caminho atual não é melhor
                
                # Criar novo estado
                estado_vizinho = Estado(
                    matriz_vizinho,
                    novo_g,
                    self.calcular_valor_h(vizinho, matriz_destino, heuristica),
                    estado_atual.get_matriz_tupla()  # Guarda o pai como a matriz em forma de tupla
                )
                
                # Adicionar à lista aberta
                heapq.heappush(lista_aberta, (estado_vizinho.c, id(estado_vizinho), estado_vizinho))
                estados_abertos[matriz_vizinho] = estado_vizinho
        
        # Não encontrou solução
        metricas.atualizar_tempo(inicio_tempo)
        return None, metricas

    def executar_experimentos(self, num_experimentos=100, limite_movimentos=30):
        """Executa experimentos para comparar diferentes heurísticas"""
        # Classe para armazenar resultados por heurística
        class ResultadosHeuristica:
            def __init__(self):
                self.nodos = []
                self.profundidade = []
                self.tempo = []
                self.solucoes = 0
                
            def adicionar_metrica(self, metrica):
                if metrica.profundidade != -1:
                    self.nodos.append(metrica.nodos_expandidos)
                    self.profundidade.append(metrica.profundidade)
                    self.tempo.append(metrica.tempo)
                    self.solucoes += 1
                    
            def to_dict(self):
                """Converte para dicionário (para compatibilidade)"""
                return {
                    "nodos": self.nodos,
                    "profundidade": self.profundidade,
                    "tempo": self.tempo,
                    "solucoes": self.solucoes
                }
        
        # Inicializar resultados para cada heurística
        resultados = {i: ResultadosHeuristica() for i in range(1, 5)}
        
        for _ in range(num_experimentos):
            # Começar com o estado objetivo
            matriz_inicial = copy.deepcopy(self.matriz_destino)
            
            # Embaralhar com movimentos válidos
            for _ in range(np.random.randint(10, limite_movimentos + 1)):
                vizinhos = self.get_vizinhos(matriz_inicial)
                if vizinhos:
                    matriz_inicial = vizinhos[np.random.randint(0, len(vizinhos))]
            
            # Garantir que é solucionável
            while not self.e_solucionavel(matriz_inicial) == self.e_solucionavel(self.matriz_destino):
                # Troque duas peças (exceto o espaço vazio)
                indices = [(i, j) for i in range(3) for j in range(3) if matriz_inicial[i, j] != 0]
                idx1, idx2 = np.random.choice(len(indices), 2, replace=False)
                i1, j1 = indices[idx1]
                i2, j2 = indices[idx2]
                matriz_inicial[i1, j1], matriz_inicial[i2, j2] = matriz_inicial[i2, j2], matriz_inicial[i1, j1]
                
            # Testar cada heurística
            for heur in range(1, 5):
                _, metricas = self.busca_a_estrela(matriz_inicial, self.matriz_destino, heur)
                resultados[heur].adicionar_metrica(metricas)
        
        # Converter resultados para o formato esperado pela função de visualização
        resultados_dict = {i: resultado.to_dict() for i, resultado in resultados.items()}
        return resultados_dict

    def mostrar_resultados(self, resultados):
        """Exibe os resultados dos experimentos em formato gráfico"""
        heuristica_nomes = {
            1: "Manhattan",
            2: "Hamming", 
            3: "Manhattan Ponderada",
            4: "Combinada"
        }
        
        # Preparar dados para comparação
        medias_nodos = [np.mean(resultados[h]["nodos"]) for h in range(1, 5)]
        medias_tempo = [np.mean(resultados[h]["tempo"]) for h in range(1, 5)]
        medias_prof = [np.mean(resultados[h]["profundidade"]) for h in range(1, 5)]
        solucoes = [resultados[h]["solucoes"] for h in range(1, 5)]
        
        # Configurar subplots
        fig, axs = plt.subplots(2, 2, figsize=(14, 10))
        heuristica_labels = list(heuristica_nomes.values())
        
        # Gráfico de nós expandidos
        axs[0, 0].bar(heuristica_labels, medias_nodos, color='skyblue')
        axs[0, 0].set_title('Média de Nós Expandidos')
        axs[0, 0].set_ylabel('Número de nós')
        
        # Gráfico de tempo
        axs[0, 1].bar(heuristica_labels, medias_tempo, color='salmon')
        axs[0, 1].set_title('Tempo Médio de Execução (segundos)')
        axs[0, 1].set_ylabel('Tempo (s)')
        
        # Gráfico de profundidade
        axs[1, 0].bar(heuristica_labels, medias_prof, color='lightgreen')
        axs[1, 0].set_title('Profundidade Média da Solução')
        axs[1, 0].set_ylabel('Profundidade')
        
        # Gráfico de soluções encontradas
        axs[1, 1].bar(heuristica_labels, solucoes, color='gold')
        axs[1, 1].set_title('Número de Soluções Encontradas')
        axs[1, 1].set_ylabel('Soluções')
        
        plt.tight_layout()
        plt.savefig('comparacao_heuristicas.png')
        plt.show()
        
        # Imprimir relatório textual
        print("\nRelatório de Desempenho das Heurísticas:")
        print("=" * 50)
        for h in range(1, 5):
            print(f"\nHeurística: {heuristica_nomes[h]}")
            print(f"Soluções encontradas: {resultados[h]['solucoes']}")
            if resultados[h]['solucoes'] > 0:
                print(f"Média de nós expandidos: {np.mean(resultados[h]['nodos']):.2f}")
                print(f"Média de profundidade: {np.mean(resultados[h]['profundidade']):.2f}")
                print(f"Tempo médio (s): {np.mean(resultados[h]['tempo']):.4f}")
        print("=" * 50)


def exibir_matriz(matriz):
    """Formata uma matriz 3x3 para exibição"""
    for i in range(3):
        print(" ".join(f"{num:2d}" if num != 0 else "  " for num in matriz[i]))
    print()

def exibir_solucao(solucao):
    """Exibe a sequência de estados da solução"""
    if not solucao:
        print("Sem solução!")
        return
        
    print(f"Solução encontrada com {len(solucao) - 1} movimentos:")
    for i, estado in enumerate(solucao):
        print(f"Passo {i}:")
        exibir_matriz(estado)
    
def main():
    print("Bem vindo a RESOLVE TUDO SLIDING PUZZLES 3X3 ULTIMATE")
    puzzle = SlidingPuzzle()  # Criar instância da classe principal

    while True:
        try:
            print("\nSelecione a opcao:")
            print("1. Resolver matriz manualmente inserida")
            print("2. Resolver matriz aleatória")
            print("3. Modo análise (comparação de heurísticas)")
            print("0. Encerrar programa")
            escolha = int(input("Sua escolha: "))
            
            if escolha not in [0, 1, 2, 3]:
                print("Escolha inválida")
                continue

            if escolha == 1 or escolha == 2:
                print("\nSelecione a heurística desejada:")
                print("1. Manhattan")
                print("2. Hamming")
                print("3. Manhattan ponderada (peso 1.5)")
                print("4. Heurísticas combinadas (manhattan e hamming)")
                heuristica = int(input("Sua escolha: "))
                
                if heuristica not in [1, 2, 3, 4]:
                    print("Heurística inválida!")
                    continue
                
                matriz_destino = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])

                if escolha == 1:
                    matriz_inicial = np.zeros((3, 3), dtype=int)
                    print("\nDigite os valores da matriz 3x3 (use 0 para o espaço vazio):")
                    for linha in range(3):
                        for coluna in range(3):
                            matriz_inicial[linha][coluna] = int(input(f"Digite o valor em [{linha}][{coluna}]: "))
                
                elif escolha == 2:
                    rng = np.random.default_rng()
                    matriz_inicial = np.arange(9)
                    rng.shuffle(matriz_inicial)
                    matriz_inicial = matriz_inicial.reshape(3, 3)
                    print("\nMatriz aleatória gerada:")
                    exibir_matriz(matriz_inicial)
                
                # Verificar se é solucionável antes de tentar resolver
                if not puzzle.e_solucionavel(matriz_inicial) == puzzle.e_solucionavel(matriz_destino):
                    print("\nAtenção: Esta configuração NÃO tem solução!")
                    continue
                    
                print("\nResolvendo...\n")
                solucao, metricas = puzzle.busca_a_estrela(matriz_inicial, matriz_destino, heuristica)
                
                if solucao is None:
                    print("Sem solução possível para esta configuração!")
                else:
                    exibir_solucao(solucao)
                    print(metricas)  # Usa o método __str__ da classe Metricas

            elif escolha == 3:
                print("\nModo Análise - Comparação de Heurísticas")
                num_experimentos = int(input("Quantos experimentos deseja executar? (recomendado: 50-100): "))
                if num_experimentos <= 0:
                    print("Número de experimentos deve ser positivo!")
                    continue
                
                print(f"\nExecutando {num_experimentos} experimentos. Isso pode levar algum tempo...")
                resultados = puzzle.executar_experimentos(num_experimentos)
                puzzle.mostrar_resultados(resultados)
                print("\nAnálise completa! Gráficos salvos em 'comparacao_heuristicas.png'")

            elif escolha == 0:
                print("Encerrando programa. Até logo!")
                break
                
        except ValueError as e:
            print(f"Erro: entrada inválida - {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()
