import numpy as np


def compute_slic_distance(y, x, cluster, image, S, m):
    """
    Calcula a distância usada no SLIC.

    A distância mistura:
    - diferença de cor/intensidade
    - distância espacial entre pixel e centro do cluster

    y, x: posição do pixel analisado
    cluster: centro atual do superpixel
    image: imagem de entrada
    S: tamanho esperado do superpixel
    m: peso da compactação espacial
    """

    yc, xc, ic = cluster

    # distância espacial
    ds2 = (y - yc) ** 2 + (x - xc) ** 2

    pixel = image[y, x]

    # distância de cor/intensidade
    if image.ndim == 2:
        dc2 = (float(pixel) - float(ic)) ** 2
    else:
        dc2 = np.sum(
            (pixel.astype(float) - np.asarray(ic, dtype=float)) ** 2
        )

    distancia = np.sqrt(dc2 + ((m / S) ** 2) * ds2)

    return distancia


def initialize_clusters(image, S):
    """
    Inicializa os clusters do SLIC em uma grade regular.

    Cada cluster guarda:
    - posição y
    - posição x
    - cor/intensidade do pixel naquela posição
    """

    altura, largura = image.shape[:2]

    clusters = []

    for y in range(S // 2, altura, S):
        for x in range(S // 2, largura, S):
            pixel = image[y, x]

            if hasattr(pixel, "astype"):
                intensidade = pixel.astype(float)
            else:
                intensidade = float(pixel)

            clusters.append([
                float(y),
                float(x),
                intensidade
            ])

    return clusters


def slic(image, num_superpixels=100, m=10, max_iter=10):
    """
    Implementação manual do algoritmo SLIC.

    O algoritmo cria superpixels agrupando pixels próximos
    em cor/intensidade e posição espacial.
    """

    altura, largura = image.shape[:2]

    # S representa o tamanho aproximado de cada superpixel
    S = max(1, int(np.sqrt((altura * largura) / num_superpixels)))

    clusters = initialize_clusters(image, S)

    quantidade_clusters = len(clusters)

    labels = -np.ones((altura, largura), dtype=np.int32)
    distances = np.full((altura, largura), np.inf)

    for _ in range(max_iter):

        for k, cluster in enumerate(clusters):
            yc, xc, _ = cluster

            y0 = int(max(yc - S, 0))
            y1 = int(min(yc + S, altura))

            x0 = int(max(xc - S, 0))
            x1 = int(min(xc + S, largura))

            for y in range(y0, y1):
                for x in range(x0, x1):
                    distancia = compute_slic_distance(
                        y,
                        x,
                        cluster,
                        image,
                        S,
                        m
                    )

                    if distancia < distances[y, x]:
                        distances[y, x] = distancia
                        labels[y, x] = k

        novos_clusters = []

        for k in range(quantidade_clusters):
            ys, xs = np.where(labels == k)

            if len(ys) == 0:
                novos_clusters.append(clusters[k])
                continue

            yc = np.mean(ys)
            xc = np.mean(xs)

            if image.ndim == 2:
                ic = np.mean(image[ys, xs])
            else:
                ic = np.mean(image[ys, xs], axis=0)

            novos_clusters.append([
                yc,
                xc,
                ic
            ])

        clusters = novos_clusters

        # reinicia as distâncias para a próxima iteração
        distances[:, :] = np.inf

    return labels


def criar_imagem_labels(labels):
    """
    Cria uma imagem visual para representar os superpixels.

    Cada label recebe uma intensidade diferente.
    Serve apenas para visualização.
    """

    altura, largura = labels.shape

    labels_normalizado = labels.copy().astype(np.float32)

    menor = np.min(labels_normalizado)
    maior = np.max(labels_normalizado)

    if maior - menor == 0:
        return np.zeros((altura, largura), dtype=np.uint8)

    labels_normalizado = (labels_normalizado - menor) / (maior - menor)
    labels_normalizado = labels_normalizado * 255

    return labels_normalizado.astype(np.uint8)


def criar_bordas_superpixels(labels):
    """
    Cria uma imagem binária com as bordas dos superpixels.

    Um pixel é borda se algum vizinho direto possui label diferente.
    """

    altura, largura = labels.shape

    bordas = np.zeros((altura, largura), dtype=np.uint8)

    for y in range(altura):
        for x in range(largura):

            label_atual = labels[y, x]

            if y + 1 < altura:
                if labels[y + 1, x] != label_atual:
                    bordas[y, x] = 255

            if x + 1 < largura:
                if labels[y, x + 1] != label_atual:
                    bordas[y, x] = 255

    return bordas


def refinar_mascara_por_superpixels(
    labels,
    mascara_inicial,
    percentual_minimo=0.35,
    modo="preencher"
):
    """
    Refina uma máscara binária usando os superpixels.

    Para cada superpixel:
    - calcula a porcentagem de pixels brancos na máscara inicial
    - se a porcentagem for maior ou igual ao limite, o superpixel é marcado como grão

    percentual_minimo:
    - 0.30 significa 30%
    - 0.50 significa 50%

    modo:
    - preencher: marca o superpixel inteiro como branco
    - intersecao: mantém apenas os pixels que já eram brancos na máscara inicial
    """

    mascara_saida = np.zeros_like(mascara_inicial)

    labels_unicos = np.unique(labels)

    for label in labels_unicos:
        if label < 0:
            continue

        regiao = labels == label

        total_pixels = np.sum(regiao)

        if total_pixels == 0:
            continue

        pixels_objeto = np.sum(mascara_inicial[regiao] > 0)

        proporcao = pixels_objeto / total_pixels

        if proporcao >= percentual_minimo:
            if modo == "preencher":
                mascara_saida[regiao] = 255

            elif modo == "intersecao":
                mascara_saida[regiao] = mascara_inicial[regiao]

            else:
                print("Modo de refinamento desconhecido:", modo)
                mascara_saida[regiao] = 255

    return mascara_saida


def aplicar_superpixels(
    img,
    mascara_inicial,
    num_superpixels=300,
    m=10,
    max_iter=5,
    percentual_minimo=0.35,
    modo="preencher"
):
    """
    Aplica SLIC e usa os superpixels para refinar a máscara inicial.

    Retorna:
    - labels dos superpixels
    - imagem visual dos labels
    - imagem das bordas dos superpixels
    - máscara refinada
    """

    labels = slic(
        img,
        num_superpixels=num_superpixels,
        m=m,
        max_iter=max_iter
    )

    imagem_labels = criar_imagem_labels(labels)

    bordas = criar_bordas_superpixels(labels)

    mascara_refinada = refinar_mascara_por_superpixels(
        labels,
        mascara_inicial,
        percentual_minimo=percentual_minimo,
        modo=modo
    )

    return labels, imagem_labels, bordas, mascara_refinada

def obter_limites_mascara(mascara):
    """
    Encontra os limites da região branca de uma máscara.
    Retorna ymin, ymax, xmin, xmax.
    """

    ys, xs = np.where(mascara > 0)

    if len(ys) == 0 or len(xs) == 0:
        return 0, mascara.shape[0], 0, mascara.shape[1]

    ymin = np.min(ys)
    ymax = np.max(ys) + 1
    xmin = np.min(xs)
    xmax = np.max(xs) + 1

    return ymin, ymax, xmin, xmax


def aplicar_superpixels_na_roi(
    img,
    mascara_roi,
    mascara_inicial,
    num_superpixels=100,
    m=10,
    max_iter=5,
    percentual_minimo=0.35,
    modo="preencher"
):
    """
    Aplica superpixels apenas na região da ROI.

    Isso evita gerar superpixels na área preta fora da placa
    e reduz o tempo de processamento.
    """

    altura, largura = mascara_inicial.shape

    ymin, ymax, xmin, xmax = obter_limites_mascara(mascara_roi)

    img_recorte = img[ymin:ymax, xmin:xmax]
    mascara_roi_recorte = mascara_roi[ymin:ymax, xmin:xmax]
    mascara_inicial_recorte = mascara_inicial[ymin:ymax, xmin:xmax]

    # Garante que fora da ROI circular fique preto também no recorte
    mascara_inicial_recorte = np.where(
        mascara_roi_recorte > 0,
        mascara_inicial_recorte,
        0
    ).astype(np.uint8)

    labels_recorte, imagem_labels_recorte, bordas_recorte, mascara_refinada_recorte = aplicar_superpixels(
        img_recorte,
        mascara_inicial_recorte,
        num_superpixels=num_superpixels,
        m=m,
        max_iter=max_iter,
        percentual_minimo=percentual_minimo,
        modo=modo
    )

    labels_completo = -np.ones((altura, largura), dtype=np.int32)
    imagem_labels_completa = np.zeros((altura, largura), dtype=np.uint8)
    bordas_completa = np.zeros((altura, largura), dtype=np.uint8)
    mascara_refinada_completa = np.zeros((altura, largura), dtype=np.uint8)

    labels_completo[ymin:ymax, xmin:xmax] = labels_recorte
    imagem_labels_completa[ymin:ymax, xmin:xmax] = imagem_labels_recorte
    bordas_completa[ymin:ymax, xmin:xmax] = bordas_recorte
    mascara_refinada_completa[ymin:ymax, xmin:xmax] = mascara_refinada_recorte

    # Remove qualquer coisa fora da ROI circular
    bordas_completa = np.where(
        mascara_roi > 0,
        bordas_completa,
        0
    ).astype(np.uint8)

    mascara_refinada_completa = np.where(
        mascara_roi > 0,
        mascara_refinada_completa,
        0
    ).astype(np.uint8)

    return labels_completo, imagem_labels_completa, bordas_completa, mascara_refinada_completa