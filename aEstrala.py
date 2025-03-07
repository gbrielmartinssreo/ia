import math
import heapq
import numpy as np

#define a classe Cell (célula)
class Cell:
    def __init__(self):
        self.parent_i=0 #indice da linha do pai da celula
        self.parent_j=0 #indice da coluna do pai da celula
        self.f=float('inf') #custo total da celula (g+h)
        self.g=float('inf') #custo do inicio ate esta celula
        self.h=0 #custo heuristico desta celula ate o destino

#define o tamanho da grade (grid)
ROW = 9
COL = 10

#verifica se uma celula eh valida (esta dentro da grade)
def is_valid(row,col):
    return (row>=0) and (row<ROW) and (col>=0) and (col<COL)

#verifica se uma celula nao esta bloqueada
def is_unblocked(grid,row,col):
    return grid[row][col]==1

#verifica se uma celula eh o destino
def is_destination(row,col,dest):
    return row==dest[0] and col == dest[1]

#calcula o valor heuristico de uma celula (distancia euclidiana até o destino)
def calculate_h_value(row,col,dest):
    return ((row-dest[0])**2+(col-dest[1])**2)**0.5

#traça o caminho do inicio até o destino
def trace_path(cell_details,dest):
    print("O caminho encontrado eh:")
    path = []
    row = dest[0]
    col = dest[1]

    #traça o caminho do destino até a origem usando as celulas pai
    while not(cell_details[row][col].parent_i==row and cell_details[row][col].parent_j==col):
        path.append((row,col))
        temp_row=cell_details[row][col].parent_i
        temp_col=cell_details[row][col].parent_j
        row=temp_row
        col=temp_col

    #adiciona a celula de origem ao caminho
    path.append((row,col))

    #inverte o caminho para exibi-lo da origem até o destino
    path.reverse()

    for i in path:
        print("->",i,end=" ")
    print()

#implementa o algoritmo de busca A*
def a_star_search(grid,src,dest):
    #verifica se a origem e o destino sao validos
    if not is_valid(src[0],src[1]) or not is_valid(dest[0],dest[1]):
        print("A origem ou o destino são inválidos")
        return

    #verifica se a origem e o destino nao estao bloqueados
    if not is_unblocked(grid,src[0],src[1]) or not is_unblocked(grid,dest[0],dest[1]):
        print("A origem ou o destino estao bloqueados")
        return

    #verifica se ja estamos no destino
    if is_destination(src[0],src[1],dest):
        print("Ja estamos no destino")
        return

    #inicializa a lista fechada(celulas ja visitadas)
    closed_list = np.full((ROW,COL),False) 

    #inicializa os detalhes de cada celula
    cell_details = np.empty((ROW, COL), dtype=object)  # Cria um array de objetos vazios
    for i in range(ROW):
        for j in range(COL):
            cell_details[i, j] = Cell()


    #configura os detalhes da celula inicial 
    i = src[0]
    j = src[1]

    #inicializa a lista aberta (celulas a serem visitadas) com a celula inicial
    open_list = []
    heapq.heappush(open_list,(0.0,i,j))

    #flag para indicar se o destino foi encontrado
    found_dest = False

    #loop principal do algoritmo A*
    while len(open_list)>0:
        #remove a celula com o menor valor de f da lista aberta
        p = heapq.heappop(open_list)

        #marca a celula como visitada
        i=p[1]
        j=p[2]
        closed_list[i][j]=True

        #para cada direcao possivel, verifica os sucessores
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dir in directions:
            new_i = i + dir[0]
            new_j = j + dir[1]

            # Se o sucessor for válido, não estiver bloqueado e ainda não tiver sido visitado
            if is_valid(new_i, new_j) and is_unblocked(grid, new_i, new_j) and not closed_list[new_i][new_j]:
                # Se o sucessor for o destino
                if is_destination(new_i, new_j, dest):
                    # Define o pai da célula de destino
                    cell_details[new_i][new_j].parent_i = i
                    cell_details[new_i][new_j].parent_j = j
                    print("A célula de destino foi encontrada")
                    # Traça e exibe o caminho do início até o destino
                    trace_path(cell_details, dest)
                    found_dest = True
                    return
                else:
                    # Calcula os novos valores de f, g e h
                    g_new = cell_details[i][j].g + 1.0
                    h_new = calculate_h_value(new_i, new_j, dest)
                    f_new = g_new + h_new

                    # Se a célula ainda não estiver na lista aberta ou o novo f for menor
                    if cell_details[new_i][new_j].f == float('inf') or cell_details[new_i][new_j].f > f_new:
                        # Adiciona a célula à lista aberta
                        heapq.heappush(open_list, (f_new, new_i, new_j))
                        # Atualiza os detalhes da célula
                        cell_details[new_i][new_j].f = f_new
                        cell_details[new_i][new_j].g = g_new
                        cell_details[new_i][new_j].h = h_new
                        cell_details[new_i][new_j].parent_i = i
                        cell_details[new_i][new_j].parent_j = j

    # Se o destino não foi encontrado após visitar todas as células
    if not found_dest:
        print("Falha ao encontrar a célula de destino")

def main():
    # Define a grade (1 para caminho livre, 0 para bloqueado)
    grid = [
        [1, 0, 1, 1, 1, 1, 0, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 1, 0, 1, 1],
        [1, 1, 1, 0, 1, 1, 0, 1, 0, 1],
        [0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1, 0, 1, 0],
        [1, 0, 1, 1, 1, 1, 0, 1, 0, 0],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 1, 1, 1],
        [1, 1, 1, 0, 0, 0, 1, 0, 0, 1]
    ]

    # Define a origem e o destino
    src = [8, 0]
    dest = [0, 0]

    # Executa o algoritmo de busca A*
    a_star_search(grid, src, dest)

if __name__ == "__main__":
    main()
