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


def separar_componentes_grandes_por_area(
    mascara,
    area_media_grao=4000,
    area_minima=100,
    iteracoes=12
):
    """
    Divide componentes grandes em subcomponentes estimando quantos graos existem
    pela area. A divisao apaga as fronteiras entre grupos e mantem a mascara binaria.
    """

    labels, componentes = rotular_componentes(mascara)
    mascara_saida = np.zeros_like(mascara)

    for componente in componentes:
        area = componente["area"]

        if area < area_minima:
            continue

        pixels = np.array(componente["pixels"], dtype=np.float64)
        quantidade_estimada = int(round(area / area_media_grao))
        quantidade_estimada = max(1, quantidade_estimada)

        yy = pixels[:, 0].astype(np.int32)
        xx = pixels[:, 1].astype(np.int32)

        if quantidade_estimada == 1:
            mascara_saida[yy, xx] = 255
            continue

        pixels_centralizados = pixels - np.mean(pixels, axis=0)
        matriz_covariancia = pixels_centralizados.T @ pixels_centralizados
        valores, vetores = np.linalg.eigh(matriz_covariancia)
        eixo_principal = vetores[:, np.argmax(valores)]
        projecao = pixels_centralizados @ eixo_principal

        percentis = np.linspace(0, 100, quantidade_estimada + 2)[1:-1]
        centros = []

        for percentil in percentis:
            alvo = np.percentile(projecao, percentil)
            indice = np.argmin(np.abs(projecao - alvo))
            centros.append(pixels[indice].copy())

        centros = np.array(centros, dtype=np.float64)

        for _ in range(iteracoes):
            distancias = np.sum(
                (pixels[:, None, :] - centros[None, :, :]) ** 2,
                axis=2
            )
            grupos = np.argmin(distancias, axis=1)
            novos_centros = centros.copy()

            for indice_grupo in range(quantidade_estimada):
                pontos_grupo = pixels[grupos == indice_grupo]

                if len(pontos_grupo) > 0:
                    novos_centros[indice_grupo] = np.mean(pontos_grupo, axis=0)

            if np.allclose(novos_centros, centros):
                break

            centros = novos_centros

        distancias = np.sum(
            (pixels[:, None, :] - centros[None, :, :]) ** 2,
            axis=2
        )
        grupos = np.argmin(distancias, axis=1) + 1

        labels_locais = np.zeros_like(labels, dtype=np.int16)
        labels_locais[yy, xx] = grupos
        fronteira = np.zeros(len(pixels), dtype=bool)

        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            novo_y = yy + dy
            novo_x = xx + dx

            dentro = (
                (novo_y >= 0) &
                (novo_y < mascara.shape[0]) &
                (novo_x >= 0) &
                (novo_x < mascara.shape[1])
            )

            vizinho = np.zeros(len(pixels), dtype=np.int16)
            vizinho[dentro] = labels_locais[novo_y[dentro], novo_x[dentro]]

            fronteira = fronteira | (
                dentro &
                (vizinho > 0) &
                (vizinho != grupos)
            )

        manter = ~fronteira
        mascara_saida[yy[manter], xx[manter]] = 255

    return remover_componentes_pequenos(
        mascara_saida,
        area_minima=area_minima
    )


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

        elif tipo == "separar_componentes_grandes_por_area":
            area_media_grao = operacao.get("area_media_grao", 4000)
            area_minima = operacao.get("area_minima", 100)
            iteracoes = operacao.get("iteracoes", 12)

            mascara_saida = separar_componentes_grandes_por_area(
                mascara_saida,
                area_media_grao=area_media_grao,
                area_minima=area_minima,
                iteracoes=iteracoes
            )

        else:
            print("Operação de pós-processamento desconhecida:", tipo)

    return mascara_saida
