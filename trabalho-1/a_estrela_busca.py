import heapq
import calcular_valor_h as funch
import array_pra_tupla as totup

def a_estrela_busca(matriz_inicial, matriz_destino):
    lista_aberta = []
    
    heuristica_estado_inicial = funch.calcular_valor_h(matriz_inicial,matriz_destino,1)
    heapq.heappush(lista_aberta,(0,heuristica_estado_inicial,totup.array_pra_tupla(matriz_inicial)))

    lista_fechada = set()





    """Implementa o A* para o Sliding Puzzle."""
    open_list = []
    initial_f_value = calcular_valor_h(matriz_inicial, matriz_destino)
    heapq.heappush(open_list, (initial_f_value, array_pra_tupla(matriz_inicial), 0))

    lista_fechada = set()
    cell_details = {array_pra_tupla(matriz_inicial): {'g': 0, 'parent': None}}

    while open_list:
        f_value, current_state_tuple, g_value = heapq.heappop(open_list)
        current_state = np.array(current_state_tuple)

        if array_pra_tupla(current_state) in lista_fechada:
            continue

        lista_fechada.add(array_pra_tupla(current_state))

        if np.array_equal(current_state, matriz_destino):
            print("Caminho encontrado!")
            return trace_path(cell_details, current_state, matriz_inicial)

        successors = get_successors(current_state)

        for successor in successors:
            successor_tuple = array_pra_tupla(successor)
            g_new = cell_details[array_pra_tupla(current_state)]['g'] + 1
            h_new = calcular_valor_h(successor, matriz_destino)
            f_new = g_new + h_new

            if successor_tuple not in cell_details or g_new < cell_details[successor_tuple]['g']:
                cell_details[successor_tuple] = {'g': g_new, 'parent': current_state}
                heapq.heappush(open_list, (f_new, successor_tuple, g_new))

    print("Caminho não encontrado.")
    return None
