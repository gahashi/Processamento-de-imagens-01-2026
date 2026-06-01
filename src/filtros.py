import numpy as np


def criar_borda_replicada(img, tamanho_borda):
    """
    Cria uma borda ao redor da imagem replicando os pixels das extremidades.
    Isso evita problemas ao aplicar filtros nas bordas da imagem.
    """

    altura, largura = img.shape[:2]

    if len(img.shape) == 2:
        img_borda = np.zeros(
            (altura + 2 * tamanho_borda, largura + 2 * tamanho_borda),
            dtype=img.dtype
        )
    else:
        canais = img.shape[2]
        img_borda = np.zeros(
            (altura + 2 * tamanho_borda, largura + 2 * tamanho_borda, canais),
            dtype=img.dtype
        )

    img_borda[
        tamanho_borda:tamanho_borda + altura,
        tamanho_borda:tamanho_borda + largura
    ] = img

    # Replica linhas superior e inferior
    for y in range(tamanho_borda):
        img_borda[y, tamanho_borda:tamanho_borda + largura] = img[0, :]
        img_borda[tamanho_borda + altura + y, tamanho_borda:tamanho_borda + largura] = img[altura - 1, :]

    # Replica colunas esquerda e direita
    for x in range(tamanho_borda):
        img_borda[:, x] = img_borda[:, tamanho_borda]
        img_borda[:, tamanho_borda + largura + x] = img_borda[:, tamanho_borda + largura - 1]

    return img_borda


def filtro_mediana(img, tamanho_kernel=3):
    """
    Aplica filtro de mediana manualmente.

    Esse filtro substitui cada pixel pela mediana da vizinhança.
    É bom para remover sujeiras e ruídos pontuais.
    """

    tamanho_borda = tamanho_kernel // 2
    img_borda = criar_borda_replicada(img, tamanho_borda)

    img_saida = np.zeros_like(img)
    altura, largura = img.shape[:2]

    if len(img.shape) == 2:
        for y in range(altura):
            for x in range(largura):
                regiao = img_borda[
                    y:y + tamanho_kernel,
                    x:x + tamanho_kernel
                ]

                img_saida[y, x] = np.median(regiao)

    else:
        canais = img.shape[2]

        for y in range(altura):
            for x in range(largura):
                for c in range(canais):
                    regiao = img_borda[
                        y:y + tamanho_kernel,
                        x:x + tamanho_kernel,
                        c
                    ]

                    img_saida[y, x, c] = np.median(regiao)

    return img_saida


def filtro_media(img, tamanho_kernel=3):
    """
    Aplica filtro de média manualmente.

    Esse filtro suaviza a imagem usando a média dos pixels vizinhos.
    """

    tamanho_borda = tamanho_kernel // 2
    img_borda = criar_borda_replicada(img, tamanho_borda)

    img_saida = np.zeros_like(img)
    altura, largura = img.shape[:2]

    if len(img.shape) == 2:
        for y in range(altura):
            for x in range(largura):
                regiao = img_borda[
                    y:y + tamanho_kernel,
                    x:x + tamanho_kernel
                ]

                img_saida[y, x] = np.uint8(np.mean(regiao))

    else:
        canais = img.shape[2]

        for y in range(altura):
            for x in range(largura):
                for c in range(canais):
                    regiao = img_borda[
                        y:y + tamanho_kernel,
                        x:x + tamanho_kernel,
                        c
                    ]

                    img_saida[y, x, c] = np.uint8(np.mean(regiao))

    return img_saida


def criar_kernel_gaussiano(tamanho_kernel=3, sigma=1.0):
    """
    Cria um kernel gaussiano manualmente.
    """

    centro = tamanho_kernel // 2
    kernel = np.zeros((tamanho_kernel, tamanho_kernel), dtype=np.float64)

    soma = 0.0

    for y in range(tamanho_kernel):
        for x in range(tamanho_kernel):
            dy = y - centro
            dx = x - centro

            valor = np.exp(-((dx ** 2 + dy ** 2) / (2 * sigma ** 2)))
            kernel[y, x] = valor
            soma += valor

    kernel = kernel / soma

    return kernel


def filtro_gaussiano(img, tamanho_kernel=3, sigma=1.0):
    """
    Aplica filtro gaussiano manualmente.

    Ele suaviza a imagem dando mais peso aos pixels próximos ao centro.
    """

    tamanho_borda = tamanho_kernel // 2
    img_borda = criar_borda_replicada(img, tamanho_borda)

    kernel = criar_kernel_gaussiano(tamanho_kernel, sigma)

    img_saida = np.zeros_like(img)
    altura, largura = img.shape[:2]

    if len(img.shape) == 2:
        for y in range(altura):
            for x in range(largura):
                regiao = img_borda[
                    y:y + tamanho_kernel,
                    x:x + tamanho_kernel
                ]

                valor = np.sum(regiao * kernel)
                img_saida[y, x] = np.uint8(np.clip(valor, 0, 255))

    else:
        canais = img.shape[2]

        for y in range(altura):
            for x in range(largura):
                for c in range(canais):
                    regiao = img_borda[
                        y:y + tamanho_kernel,
                        x:x + tamanho_kernel,
                        c
                    ]

                    valor = np.sum(regiao * kernel)
                    img_saida[y, x, c] = np.uint8(np.clip(valor, 0, 255))

    return img_saida


def aplicar_filtros(img, lista_filtros):
    """
    Aplica uma lista de filtros na imagem.

    Cada filtro deve ser informado como dicionário.

    Exemplo:
    {
        "tipo": "mediana",
        "tamanho_kernel": 5
    }
    """

    img_saida = img.copy()

    for filtro in lista_filtros:
        tipo = filtro["tipo"]

        if tipo == "mediana":
            tamanho_kernel = filtro.get("tamanho_kernel", 3)
            img_saida = filtro_mediana(img_saida, tamanho_kernel)

        elif tipo == "media":
            tamanho_kernel = filtro.get("tamanho_kernel", 3)
            img_saida = filtro_media(img_saida, tamanho_kernel)

        elif tipo == "gaussiano":
            tamanho_kernel = filtro.get("tamanho_kernel", 3)
            sigma = filtro.get("sigma", 1.0)
            img_saida = filtro_gaussiano(img_saida, tamanho_kernel, sigma)

        else:
            print("Filtro desconhecido:", tipo)

    return img_saida