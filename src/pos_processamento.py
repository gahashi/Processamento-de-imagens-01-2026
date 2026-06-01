import numpy as np
from collections import deque


def ponto_valido(mascara, y, x, visitado):
    """
    Verifica se um ponto pode ser visitado durante a busca.
    """

    altura, largura = mascara.shape

    if y < 0 or y >= altura:
        return False

    if x < 0 or x >= largura:
        return False

    if visitado[y, x] == 1:
        return False

    if mascara[y, x] == 0:
        return False

    return True


def rotular_componentes(mascara):
    """
    Rotula componentes conectados manualmente usando busca em largura.

    Pixels brancos pertencem aos objetos.
    Pixels pretos pertencem ao fundo.
    """

    altura, largura = mascara.shape

    labels = np.zeros((altura, largura), dtype=np.int32)
    visitado = np.zeros((altura, largura), dtype=np.uint8)

    componentes = []
    label_atual = 0

    vizinhos = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1)
    ]

    for y in range(altura):
        for x in range(largura):
            if mascara[y, x] == 0 or visitado[y, x] == 1:
                continue

            label_atual += 1

            fila = deque()
            fila.append((y, x))
            visitado[y, x] = 1

            pixels = []

            while len(fila) > 0:
                atual_y, atual_x = fila.popleft()

                labels[atual_y, atual_x] = label_atual
                pixels.append((atual_y, atual_x))

                for dy, dx in vizinhos:
                    novo_y = atual_y + dy
                    novo_x = atual_x + dx

                    if ponto_valido(mascara, novo_y, novo_x, visitado):
                        visitado[novo_y, novo_x] = 1
                        fila.append((novo_y, novo_x))

            componentes.append({
                "label": label_atual,
                "area": len(pixels),
                "pixels": pixels
            })

    return labels, componentes


def remover_componentes_pequenos(mascara, area_minima=100):
    """
    Remove componentes pequenos da máscara binária.
    """

    labels, componentes = rotular_componentes(mascara)

    mascara_saida = np.zeros_like(mascara)

    for componente in componentes:
        if componente["area"] >= area_minima:
            for y, x in componente["pixels"]:
                mascara_saida[y, x] = 255

    return mascara_saida


def contar_componentes(mascara, area_minima=1):
    """
    Conta quantos componentes existem na máscara.
    """

    labels, componentes = rotular_componentes(mascara)

    total = 0

    for componente in componentes:
        if componente["area"] >= area_minima:
            total += 1

    return total


def aplicar_pos_processamento(mascara, lista_operacoes):
    """
    Aplica uma lista de operações de pós-processamento.

    Exemplo:
    {
        "tipo": "remover_componentes_pequenos",
        "area_minima": 300
    }
    """

    mascara_saida = mascara.copy()

    for operacao in lista_operacoes:
        tipo = operacao["tipo"]

        if tipo == "remover_componentes_pequenos":
            area_minima = operacao.get("area_minima", 100)

            mascara_saida = remover_componentes_pequenos(
                mascara_saida,
                area_minima
            )

        else:
            print("Operação de pós-processamento desconhecida:", tipo)

    return mascara_saida