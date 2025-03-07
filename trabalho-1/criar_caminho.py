def criar_caminho(, dest, start):
    caminho = []
    atual = array_pra_tupla(dest)

    while current is not None:
        path.append(np.array(current))
        current = cell_details[current]['parent']
        if current is not None:
            current = array_pra_tupla(current)

    path.reverse()
    return path
